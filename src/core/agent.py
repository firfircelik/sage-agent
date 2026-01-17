"""
Core Agent class for Sage Agent system.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class WorkflowType(Enum):
    """Workflow types"""

    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"


class AgentType(Enum):
    """Agent types"""

    MANAGER = "manager"
    SPECIALIST = "specialist"


@dataclass
class Memory:
    """Agent memory system for storing project history and knowledge."""

    projects: List[Dict] = field(default_factory=list)
    knowledge_base: Dict = field(default_factory=dict)

    def add_project(self, project_name: str, details: Dict):
        """Add project to memory."""
        self.projects.append(
            {
                "name": project_name,
                "details": details,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def recall_similar_project(self, query: str) -> Optional[Dict]:
        """Recall similar project from memory."""
        for project in self.projects:
            if query.lower() in project["name"].lower():
                return project
        return None

    def add_knowledge(self, key: str, value: str):
        """Add knowledge to knowledge base."""
        self.knowledge_base[key] = value


@dataclass
class Agent:
    """Base Agent class for Sage Agent system."""

    name: str
    role: str
    goal: str
    backstory: str
    agent_type: AgentType = AgentType.SPECIALIST
    memory: Memory = field(default_factory=Memory)
    tools: List[str] = field(default_factory=list)

    def __str__(self):
        return f"{self.name} ({self.role})"

    def think(self, task_description: str) -> str:
        """Think about a task."""
        return f"{self.name} thinking: {task_description}"

    def act(self, action: str) -> str:
        """Execute an action."""
        return f"{self.name} executing: {action}"
