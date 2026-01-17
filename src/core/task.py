"""
Task class for multi-agent system.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from .agent import Agent


@dataclass
class Task:
    """Task definition for agents to execute."""
    
    description: str
    agent: Agent
    expected_output: str
    dependencies: List[str] = None
    priority: int = 1
    
    def __post_init__(self):
        self.dependencies = self.dependencies or []
        self.status = "pending"
        self.result = None
        self.created_at = datetime.now()
        self.completed_at = None
    
    def execute(self) -> str:
        """Execute the task."""
        self.status = "in_progress"
        
        print(f"\n{'─'*60}")
        print(f"📋 TASK: {self.description}")
        print(f"👤 Assigned to: {self.agent.name}")
        print(f"🎯 Expected Output: {self.expected_output}")
        print(f"⚡ Priority: {self.priority}")
        print(f"{'─'*60}")
        
        # Agent thinks
        thought = self.agent.think(self.description)
        print(f"💭 {thought}")
        
        # Agent acts
        action = self.agent.act(self.expected_output)
        print(f"🔧 {action}")
        
        # Task completed
        self.result = f"{self.agent.name} completed: {self.expected_output}"
        self.status = "completed"
        self.completed_at = datetime.now()
        
        print(f"✅ Result: {self.result}")
        return self.result
