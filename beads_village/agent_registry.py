"""
Agent Registry - Track online agents across workspaces and teams
"""
import json
import os
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Optional, List
from datetime import datetime


@dataclass
class AgentInfo:
    """Information about a registered agent"""
    agent_id: str
    team: str
    role: Optional[str]
    workspace: str
    is_leader: bool
    current_task: Optional[str] = None
    last_seen: float = 0.0
    started_at: float = 0.0
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AgentInfo':
        return cls(**data)
    
    @property
    def is_online(self) -> bool:
        """Agent is online if seen in last 5 minutes"""
        return time.time() - self.last_seen < 300
    
    @property
    def status(self) -> str:
        """Get agent status: online, working, offline"""
        if not self.is_online:
            return 'offline'
        if self.current_task:
            return 'working'
        return 'online'


class AgentRegistry:
    """
    Registry for tracking active agents.
    Stores data in .beads-village/agents.json
    """
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = os.getcwd()
        self.base_path = Path(base_path)
        self.registry_dir = self.base_path / '.beads-village'
        self.registry_file = self.registry_dir / 'agents.json'
    
    def _ensure_dir(self):
        """Ensure registry directory exists"""
        self.registry_dir.mkdir(parents=True, exist_ok=True)
    
    def _load(self) -> Dict[str, dict]:
        """Load registry from file"""
        if not self.registry_file.exists():
            return {}
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save(self, agents: Dict[str, dict]):
        """Save registry to file"""
        self._ensure_dir()
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(agents, f, indent=2)
    
    def register(self, agent: AgentInfo) -> None:
        """Register or update an agent"""
        agents = self._load()
        agent.last_seen = time.time()
        if agent.started_at == 0:
            agent.started_at = time.time()
        agents[agent.agent_id] = agent.to_dict()
        self._save(agents)
    
    def heartbeat(self, agent_id: str) -> bool:
        """Update agent's last_seen timestamp"""
        agents = self._load()
        if agent_id in agents:
            agents[agent_id]['last_seen'] = time.time()
            self._save(agents)
            return True
        return False
    
    def update_task(self, agent_id: str, task_id: Optional[str]) -> bool:
        """Update agent's current task"""
        agents = self._load()
        if agent_id in agents:
            agents[agent_id]['current_task'] = task_id
            agents[agent_id]['last_seen'] = time.time()
            self._save(agents)
            return True
        return False
    
    def unregister(self, agent_id: str) -> bool:
        """Remove agent from registry"""
        agents = self._load()
        if agent_id in agents:
            del agents[agent_id]
            self._save(agents)
            return True
        return False
    
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get a specific agent"""
        agents = self._load()
        if agent_id in agents:
            return AgentInfo.from_dict(agents[agent_id])
        return None
    
    def get_all_agents(self) -> List[AgentInfo]:
        """Get all registered agents"""
        agents = self._load()
        return [AgentInfo.from_dict(a) for a in agents.values()]
    
    def get_active_agents(self, max_age: int = 300) -> List[AgentInfo]:
        """Get agents seen within max_age seconds"""
        now = time.time()
        agents = self._load()
        return [
            AgentInfo.from_dict(a) for a in agents.values()
            if now - a.get('last_seen', 0) < max_age
        ]
    
    def get_team_agents(self, team: str, active_only: bool = True) -> List[AgentInfo]:
        """Get agents in a specific team"""
        if active_only:
            agents = self.get_active_agents()
        else:
            agents = self.get_all_agents()
        return [a for a in agents if a.team == team]
    
    def get_teams(self) -> List[str]:
        """Get list of all teams with active agents"""
        agents = self.get_active_agents()
        return list(set(a.team for a in agents))
    
    def cleanup_stale(self, max_age: int = 3600) -> int:
        """Remove agents not seen for max_age seconds (default 1 hour)"""
        now = time.time()
        agents = self._load()
        stale = [
            agent_id for agent_id, data in agents.items()
            if now - data.get('last_seen', 0) > max_age
        ]
        for agent_id in stale:
            del agents[agent_id]
        if stale:
            self._save(agents)
        return len(stale)
    
    def get_stats(self) -> dict:
        """Get registry statistics"""
        all_agents = self.get_all_agents()
        active = [a for a in all_agents if a.is_online]
        working = [a for a in active if a.current_task]
        teams = set(a.team for a in active)
        
        return {
            'total_registered': len(all_agents),
            'active': len(active),
            'working': len(working),
            'idle': len(active) - len(working),
            'offline': len(all_agents) - len(active),
            'teams': list(teams),
            'team_count': len(teams)
        }


# Singleton instance
_registry: Optional[AgentRegistry] = None

def get_registry(base_path: str = None) -> AgentRegistry:
    """Get or create the agent registry singleton"""
    global _registry
    if _registry is None or (base_path and str(_registry.base_path) != base_path):
        _registry = AgentRegistry(base_path)
    return _registry
