"""HTTP/SSE Server for Beads Village MCP (FastAPI).

Provides HTTP server support for MCP clients (like Letta Cloud).
Uses FastAPI for better validation and documentation.

Transport:
- SSE (GET /mcp): Server-Sent Events for server->client messages.
- HTTP (POST /mcp): JSON-RPC 2.0 for client->server messages.

Usage:
    python -m beads_village.http_server --port 8080
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Union

# Try to import web framework
try:
    import uvicorn
    from fastapi import FastAPI, Request, status
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, Response
    from pydantic import BaseModel, Field
    from sse_starlette.sse import EventSourceResponse
    HAS_WEB = True
except ImportError:
    HAS_WEB = False

# Import server tools
from .server import (
    TOOLS, AGENT, WS, TEAM,
    tool_init, tool_claim, tool_done, tool_add, tool_ls, tool_show,
    tool_reserve, tool_release, tool_reservations,
    tool_msg, tool_inbox, tool_status, tool_sync, tool_cleanup, tool_doctor,
    tool_assign, tool_bv_insights, tool_bv_plan, tool_bv_priority, tool_bv_diff,
    tool_village_tui, j
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("beads-village")

# Map tool names to functions
TOOL_FUNCTIONS = {
    "init": tool_init,
    "claim": tool_claim,
    "done": tool_done,
    "add": tool_add,
    "ls": tool_ls,
    "show": tool_show,
    "reserve": tool_reserve,
    "release": tool_release,
    "reservations": tool_reservations,
    "msg": tool_msg,
    "inbox": tool_inbox,
    "status": tool_status,
    "sync": tool_sync,
    "cleanup": tool_cleanup,
    "doctor": tool_doctor,
    "assign": tool_assign,
    "bv_insights": tool_bv_insights,
    "bv_plan": tool_bv_plan,
    "bv_priority": tool_bv_priority,
    "bv_diff": tool_bv_diff,
    "village_tui": tool_village_tui,
}

# --- Pydantic Models for JSON-RPC ---

class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None

class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None

# --- Logic ---

# --- Logic ---

def preprocess_args(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Clean up arguments commonly malformed by LLMs."""
    # Fix 'paths' or 'deps' or 'tags' being JSON string instead of list
    for list_field in ["paths", "deps", "tags"]:
        if list_field in args and isinstance(args[list_field], str):
            # If it looks like a JSON list, try to parse it
            if args[list_field].strip().startswith("["):
                try:
                    parsed = json.loads(args[list_field])
                    if isinstance(parsed, list):
                        args[list_field] = parsed
                except json.JSONDecodeError:
                    pass
    
    # Fix 'ttl' being string with units
    if "ttl" in args:
        val = args["ttl"]
        if isinstance(val, str):
            # Try plain int conversion first
            if val.isdigit():
                args["ttl"] = int(val)
            else:
                # Handle suffixes
                try:
                    val = val.lower().strip()
                    mult = 1
                    if val.endswith("h"):
                        mult = 3600
                        val = val[:-1]
                    elif val.endswith("m"):
                        mult = 60
                        val = val[:-1]
                    elif val.endswith("s"):
                        val = val[:-1]
                    
                    args["ttl"] = int(float(val) * mult)
                except ValueError:
                    pass 
                    
    return args

async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Any:
    """Execute a tool call and return result."""
    if name not in TOOL_FUNCTIONS:
        raise ValueError(f"Unknown tool: {name}")
    
    logger.info(f"TOOL CALL: {name} args={json.dumps(arguments)}")

    # Preprocess arguments to fix common LLM mistakes
    arguments = preprocess_args(name, arguments)

    fn = TOOL_FUNCTIONS[name]
    if asyncio.iscoroutinefunction(fn):
        result = await fn(arguments)
    else:
        result = fn(arguments)
        
    # Parse JSON string result if needed (some tools return compact json string)
    parsed_result = result
    if isinstance(result, str):
        try:
            parsed_result = json.loads(result)
        except json.JSONDecodeError:
            parsed_result = {"output": result}
            
    # Log truncated result
    res_str = json.dumps(parsed_result)
    if len(res_str) > 200:
        res_str = res_str[:200] + "... (truncated)"
    logger.info(f"TOOL RESULT: {name} -> {res_str}")
            
    return parsed_result

def create_app() -> "FastAPI":
    app = FastAPI(
        title="Beads Village MCP",
        description="Multi-agent coordination server for Letta/MCP",
        version="1.4.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "agent": AGENT,
            "workspace": WS,
            "team": TEAM,
            "tools_count": len(TOOLS)
        }

    # -- SSE Endpoint --
    @app.get("/mcp")
    async def mcp_sse(request: Request):
        """MCP SSE endpoint."""
        async def event_generator():
            # Send the endpoint event.
            # CRITICAL FIX: Data must be the URI string for POST requests, NOT a JSON object.
            # The client uses this URI to send JSON-RPC messages.
            yield {
                "event": "endpoint",
                "data": "/mcp"
            }
            
            logger.info("New SSE connection established")
            
            while True:
                # Keep-alive
                if await request.is_disconnected():
                    logger.info("SSE connection closed")
                    break
                yield {
                    "event": "ping",
                    "data": "{}"
                }
                await asyncio.sleep(15)

        return EventSourceResponse(event_generator())

    # -- POST Endpoint (JSON-RPC) --
    @app.post("/mcp")
    async def mcp_post(request: JsonRpcRequest):
        """Handle JSON-RPC messages."""
        logger.info(f"Received JSON-RPC: method={request.method} id={request.id}")
        
        try:
            if request.method == "tools/list":
                tools_list = []
                for name, config in TOOLS.items():
                    tools_list.append({
                        "name": name,
                        "description": config.get("desc", ""),
                        "inputSchema": config.get("input", {}),
                    })
                return {
                    "jsonrpc": "2.0",
                    "id": request.id,
                    "result": {
                        "tools": tools_list
                    }
                }
            
            elif request.method == "tools/call":
                params = request.params or {}
                name = params.get("name")
                arguments = params.get("arguments", {})
                
                if not name:
                    raise ValueError("Missing 'name' in params")

                result = await handle_tool_call(name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result)}
                        ]
                    }
                }

            elif request.method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request.id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {
                            "name": "beads-village",
                            "version": "1.4.0"
                        },
                        "capabilities": {
                            "tools": {}
                        }
                    }
                }
                
            elif request.method == "notifications/initialized":
                # Notification, no response needed
                return Response(status_code=200)

            else:
                # Method not found
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": request.id,
                        "error": {"code": -32601, "message": f"Method not found: {request.method}"}
                    },
                    status_code=200 # typically JSON-RPC errors are 200 OK HTTP but with error body, or 400
                    # Standard varies, but often 200 is safest for clients parsing JSON
                )

        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request.id,
                    "error": {"code": -32000, "message": str(e)}
                },
                status_code=200
            )

    return app

def main():
    if not HAS_WEB:
        print("Error: FastAPI/Uvicorn not found. Install with: pip install beads-village[http]", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    print(f"Starting Beads Village (FastAPI) on http://{args.host}:{args.port}")
    print(f"MCP SSE Endpoint: http://{args.host}:{args.port}/mcp")
    
    app = create_app()
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
