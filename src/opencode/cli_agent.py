"""
OpenCode CLI agent for managing OpenCode commands.
"""

import subprocess  # nosec B404
import json
import os
import shlex
from typing import Optional, Dict, List
from dataclasses import dataclass
from ..llm import LLMAgent, LLMProvider
from ..core import AgentType, Memory


@dataclass
class OpenCodeCommand:
    """OpenCode CLI command definition."""

    name: str
    description: str
    command: str
    args: Dict[str, str] = None
    flags: List[str] = None

    def build(self) -> str:
        """Build command string."""
        cmd = f"opencode {self.command}"

        if self.args:
            for key, value in self.args.items():
                cmd += f" --{key} {value}"

        if self.flags:
            for flag in self.flags:
                cmd += f" {flag}"

        return cmd


class OpenCodeCLIAgent(LLMAgent):
    """Agent for managing OpenCode CLI operations."""

    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        llm_provider: Optional[LLMProvider] = None,
        agent_type: AgentType = AgentType.SPECIALIST,
        memory: Optional[Memory] = None,
        tools: list = None,
    ):
        super().__init__(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            llm_provider=llm_provider,
            agent_type=agent_type,
            memory=memory or Memory(),
            tools=tools or [],
        )

        self.opencode_commands = []
        self._register_default_commands()

    def _register_default_commands(self):
        """Register default OpenCode commands."""
        self.opencode_commands = [
            OpenCodeCommand(
                name="list_models",
                description="List available models",
                command="models",
            ),
            OpenCodeCommand(
                name="list_agents",
                description="List available agents",
                command="agent list",
            ),
            OpenCodeCommand(
                name="list_sessions",
                description="List sessions",
                command="session list",
            ),
            OpenCodeCommand(
                name="auth_login", description="Login to provider", command="auth login"
            ),
            OpenCodeCommand(
                name="mcp_list", description="List MCP servers", command="mcp list"
            ),
            OpenCodeCommand(
                name="session_stats",
                description="Get session statistics",
                command="session stats",
            ),
        ]

    def run_opencode_command(self, command_name: str, **kwargs) -> str:
        """Run OpenCode CLI command."""
        cmd = None
        for c in self.opencode_commands:
            if c.name == command_name:
                cmd = c
                break

        if not cmd:
            return f"❌ Command not found: {command_name}"

        full_cmd = cmd.build()

        for key, value in kwargs.items():
            full_cmd += f" --{key} {value}"

        try:
            print(f"🔧 Running: {full_cmd}")
            cmd_list = shlex.split(full_cmd)
            result = subprocess.run(
                cmd_list, capture_output=True, text=True, timeout=30
            )  # nosec

            if result.returncode == 0:
                return f"✅ Success:\n{result.stdout}"
            else:
                return f"❌ Error:\n{result.stderr}"
        except subprocess.TimeoutExpired:
            return "❌ Command timeout"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def list_models(self, provider: Optional[str] = None) -> str:
        """List available models."""
        cmd = ["opencode", "models"]
        if provider:
            cmd.append(provider)

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )  # nosec
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def list_agents(self) -> str:
        """List available agents."""
        return self.run_opencode_command("list_agents")

    def list_sessions(self, max_count: int = 10) -> str:
        """List sessions."""
        cmd = ["opencode", "session", "list", "--max-count", str(max_count)]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )  # nosec
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def get_session_stats(self, days: Optional[int] = None) -> str:
        """Get session statistics."""
        cmd = ["opencode", "session", "stats"]
        if days:
            cmd += ["--days", str(days)]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )  # nosec
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def run_prompt(self, prompt: str, model: Optional[str] = None) -> str:
        """Run prompt with OpenCode."""
        cmd = ["opencode", "run", prompt]
        if model:
            cmd += ["--model", model]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )  # nosec
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def analyze_opencode_config(self) -> str:
        """Analyze OpenCode configuration."""
        config_paths = [
            os.path.expanduser("~/.config/opencode/opencode.json"),
            os.path.expanduser("./.opencode/opencode.json"),
        ]

        analysis = "📋 OpenCode Configuration Analysis:\n"
        analysis += "=" * 60 + "\n"

        for path in config_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        config = json.load(f)
                    analysis += f"\n📁 {path}:\n"
                    analysis += json.dumps(config, indent=2)
                except Exception as e:
                    analysis += f"\n❌ Failed to read {path}: {e}"
            else:
                analysis += f"\n⚠️  {path} not found"

        return analysis

    def think_about_opencode(self, task: str) -> str:
        """Think about OpenCode task with LLM."""
        if not self.llm_provider:
            return super().think(task)

        system_prompt = self._build_system_prompt()

        prompt = f"""Think about and analyze the following OpenCode task:

{task}

OpenCode CLI Features:
- Commands: tui, run, serve, web, agent, auth, mcp, session, models
- Plugins: Extensible with JavaScript/TypeScript
- Custom Tools: Tools that LLM can call
- MCP Servers: Model Context Protocol servers
- Agents: Create custom agents

Please explain your strategy for this task."""

        response = self.llm_provider.generate(prompt, system_prompt)
        return f"💭 {self.name} thinking:\n{response}"
