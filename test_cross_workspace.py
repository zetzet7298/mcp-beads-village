#!/usr/bin/env python3
"""Test cross-workspace features for mcp-beads-village.

Tests:
1. Global mail directory creation
2. Agent registry functions
3. discover_workspaces() 
4. Broadcast/msg with global flag
5. inbox with global messages
6. Team switching at runtime
"""

import os
import sys
import json
import tempfile
import shutil

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing cross-workspace features")
print("=" * 60)

passed = 0
failed = 0

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"[OK] {name}")
        passed += 1
    else:
        print(f"[FAIL] {name}")
        if detail:
            print(f"       {detail}")
        failed += 1

# Test 1: Import new functions
print("\n=== Test 1: New imports ===")
try:
    from beads_village.server import (
        global_mail_dir,
        agent_registry_dir,
        register_agent,
        get_active_agents,
        discover_workspaces,
        update_agent_heartbeat,
        get_available_teams,
        _get_team_mail_dir,
        _get_team_registry_dir,
        BEADS_VILLAGE_BASE,
    )
    test("New functions imported", True)
except ImportError as e:
    test("New functions imported", False, str(e))
    sys.exit(1)

# Test 2: Global mail hub configuration
print("\n=== Test 2: Global Mail Hub ===")
test("BEADS_VILLAGE_BASE configured", BEADS_VILLAGE_BASE is not None)
test("BEADS_VILLAGE_BASE path format", ".beads-village" in BEADS_VILLAGE_BASE)
mail_dir_test = _get_team_mail_dir("test-team")
test("_get_team_mail_dir works", "test-team" in mail_dir_test and "mail" in mail_dir_test)

# Test 3: Agent registry configuration
print("\n=== Test 3: Agent Registry ===")
reg_dir_test = _get_team_registry_dir("test-team")
test("_get_team_registry_dir works", "test-team" in reg_dir_test and "agents" in reg_dir_test)

# Test 4: New tools in TOOLS registry
print("\n=== Test 4: New Tools ===")
from beads_village.server import TOOLS
test("broadcast tool exists", "broadcast" in TOOLS)
test("discover tool exists", "discover" in TOOLS)

# Check msg tool has global parameter
msg_props = TOOLS.get("msg", {}).get("input", {}).get("properties", {})
test("msg has global param", "global" in msg_props)

# Check inbox tool has global parameter
inbox_props = TOOLS.get("inbox", {}).get("input", {}).get("properties", {})
test("inbox has global param", "global" in inbox_props)

# Check init tool has team parameter
init_props = TOOLS.get("init", {}).get("input", {}).get("properties", {})
test("init has team param", "team" in init_props)

# Test 5: Tool functions exist
print("\n=== Test 5: Tool Functions ===")
from beads_village.server import tool_broadcast, tool_discover
test("tool_broadcast exists", callable(tool_broadcast))
test("tool_discover exists", callable(tool_discover))

# Test 6: Directory creation functions
print("\n=== Test 6: Directory Functions ===")
# Use temp directory to test
with tempfile.TemporaryDirectory() as tmpdir:
    # Temporarily override the global paths
    import beads_village.server as srv
    old_base = srv.BEADS_VILLAGE_BASE
    old_team = srv.TEAM
    
    srv.BEADS_VILLAGE_BASE = tmpdir
    srv.TEAM = "test-team"
    
    try:
        # Test global_mail_dir creates directory
        mail_path = global_mail_dir()
        test("global_mail_dir creates directory", os.path.isdir(mail_path))
        test("global_mail_dir uses team", "test-team" in mail_path)
        
        # Test agent_registry_dir creates directory
        reg_path = agent_registry_dir()
        test("agent_registry_dir creates directory", os.path.isdir(reg_path))
        test("agent_registry_dir uses team", "test-team" in reg_path)
        
        # Test register_agent
        srv.AGENT = "test-agent-123"
        srv.WS = tmpdir
        result = register_agent(capabilities=["backend", "api"])
        test("register_agent returns dict", isinstance(result, dict))
        test("register_agent includes agent", result.get("agent") == "test-agent-123")
        test("register_agent includes capabilities", "backend" in result.get("capabilities", []))
        
        # Check file was created
        reg_file = os.path.join(reg_path, "test-agent-123.json")
        test("agent registry file created", os.path.exists(reg_file))
        
        # Test get_active_agents
        agents = get_active_agents()
        test("get_active_agents returns list", isinstance(agents, list))
        test("get_active_agents finds our agent", any(a.get("agent") == "test-agent-123" for a in agents))
        
        # Test discover_workspaces
        workspaces = discover_workspaces()
        test("discover_workspaces returns list", isinstance(workspaces, list))
        
        # Test get_available_teams
        # Create another team directory
        os.makedirs(os.path.join(tmpdir, "another-team", "mail"), exist_ok=True)
        teams = get_available_teams()
        test("get_available_teams returns list", isinstance(teams, list))
        test("get_available_teams finds teams", len(teams) >= 1)
        
    finally:
        srv.BEADS_VILLAGE_BASE = old_base
        srv.TEAM = old_team

# Test 7: Status tool includes new fields
print("\n=== Test 7: Status Tool ===")
status_fn = TOOLS.get("status", {}).get("fn")
test("status tool exists", status_fn is not None)
# Check description mentions agents
status_desc = TOOLS.get("status", {}).get("desc", "")
test("status mentions agents", "agent" in status_desc.lower())

# Test 8: Init tool description mentions team
print("\n=== Test 8: Init Tool ===")
init_desc = TOOLS.get("init", {}).get("desc", "")
test("init mentions team", "team" in init_desc.lower())

print("\n" + "=" * 60)
print(f"Results: {passed} passed, {failed} failed")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
