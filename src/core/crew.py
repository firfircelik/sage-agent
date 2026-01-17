"""
Crew class for orchestrating agents and tasks.
"""

from typing import List, Dict
from datetime import datetime
from .agent import Agent, WorkflowType
from .task import Task


class Crew:
    """Orchestrates agents and tasks in the Sage Agent system."""

    def __init__(
        self,
        agents: List[Agent],
        tasks: List[Task],
        workflow_type: WorkflowType = WorkflowType.SEQUENTIAL,
        verbose: bool = True,
        project_name: str = "Unnamed Project",
    ):
        self.agents = agents
        self.tasks = tasks
        self.workflow_type = workflow_type
        self.verbose = verbose
        self.project_name = project_name
        self.execution_log = []
        self.start_time = None
        self.end_time = None

    def _sort_tasks_by_priority(self):
        """Sort tasks by priority."""
        self.tasks.sort(key=lambda t: t.priority, reverse=True)

    def _check_dependencies(self, task: Task) -> bool:
        """Check if task dependencies are satisfied."""
        for dep in task.dependencies:
            for log in self.execution_log:
                if log["task"] == dep and log["status"] != "completed":
                    return False
        return True

    def kickoff(self) -> Dict:
        """Start the crew and execute all tasks."""
        self.start_time = datetime.now()

        print("\n" + "=" * 60)
        print("🚀 SAGE AGENT SYSTEM STARTED")
        print("=" * 60)
        print(f"📌 Project: {self.project_name}")
        print(f"🔄 Workflow: {self.workflow_type.value}")
        print(f"👥 Team Members: {len(self.agents)}")
        for agent in self.agents:
            print(f"   - {agent} [{agent.agent_type.value}]")
        print(f"📋 Total Tasks: {len(self.tasks)}")
        print("=" * 60 + "\n")

        # Sort tasks by priority
        self._sort_tasks_by_priority()

        results = {}
        completed_count = 0

        for i, task in enumerate(self.tasks, 1):
            # Check dependencies
            if not self._check_dependencies(task):
                print(
                    f"\n⏸️  [{i}/{len(self.tasks)}] Task dependencies not met: {task.description}"
                )
                continue

            print(f"\n[{i}/{len(self.tasks)}] Starting task...")
            result = task.execute()
            results[task.description] = result

            self.execution_log.append(
                {
                    "task": task.description,
                    "agent": task.agent.name,
                    "status": task.status,
                    "result": result,
                    "priority": task.priority,
                    "duration": (task.completed_at - task.created_at).total_seconds(),
                }
            )

            completed_count += 1

        self.end_time = datetime.now()

        print("\n" + "=" * 60)
        print("✨ ALL TASKS COMPLETED")
        print("=" * 60)
        print(
            f"⏱️  Total Time: {(self.end_time - self.start_time).total_seconds():.2f}s"
        )
        print(f"✅ Completed: {completed_count}/{len(self.tasks)}")
        print("=" * 60 + "\n")

        return results

    def generate_report(self) -> str:
        """Generate execution report."""
        report = f"""
{'='*60}
📊 PROJECT SUMMARY REPORT
{'='*60}
Project: {self.project_name}
Workflow: {self.workflow_type.value}
Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
End: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}
Total Time: {(self.end_time - self.start_time).total_seconds():.2f}s

{'─'*60}
TASK DETAILS
{'─'*60}
"""

        for i, log in enumerate(self.execution_log, 1):
            report += f"""
{i}. {log['task']}
   Assigned to: {log['agent']}
   Status: {log['status']}
   Priority: {log['priority']}
   Duration: {log['duration']:.2f}s
   Result: {log['result']}
"""

        report += f"""
{'='*60}
✅ Total Completed: {len(self.execution_log)}
{'='*60}
"""
        return report
