"""
Advanced OpenCode CLI Agent with full integration capabilities.
"""

import subprocess
import json
import os
import asyncio
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from ..llm import LLMAgent, LLMProvider
from ..rlm import RLMEnabledLLMAgent
from ..core import AgentType, Memory, Task, Crew, WorkflowType


@dataclass
class OpenCodeModel:
    """OpenCode model information."""
    name: str
    provider: str
    available: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OpenCodeAgent:
    """OpenCode agent information."""
    name: str
    description: str
    tools: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdvancedOpenCodeCLIAgent(RLMEnabledLLMAgent):
    """Advanced OpenCode CLI agent with full capabilities."""
    
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
        enable_rlm: bool = True,
        opencode_config_dir: str = "~/.config/opencode"
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
            enable_rlm=enable_rlm,
            cache_responses=True
        )
        
        self.opencode_config_dir = os.path.expanduser(opencode_config_dir)
        self.available_models: List[OpenCodeModel] = []
        self.available_agents: List[OpenCodeAgent] = []
        self._load_opencode_info()
    
    def _load_opencode_info(self):
        """Load OpenCode models and agents."""
        try:
            # Load models
            result = subprocess.run(
                ["opencode", "models"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self._parse_models(result.stdout)
                # Also update ModelRegistry
                self._update_model_registry(result.stdout)
            
            # Load agents
            result = subprocess.run(
                ["opencode", "agent", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self._parse_agents(result.stdout)
        except Exception as e:
            print(f"⚠️  Could not load OpenCode info: {e}")
    
    def _update_model_registry(self, output: str):
        """Update global model registry with OpenCode models."""
        try:
            from ..utils import ModelRegistry
            registry = ModelRegistry(auto_discover_opencode=False)
            registry._parse_opencode_models(output)
        except Exception:
            pass
    
    def _parse_models(self, output: str):
        """Parse models from OpenCode output."""
        lines = output.split("\n")
        for line in lines:
            if line.strip() and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    model = OpenCodeModel(
                        name=parts[0],
                        provider=parts[1] if len(parts) > 1 else "unknown"
                    )
                    self.available_models.append(model)
    
    def _parse_agents(self, output: str):
        """Parse agents from OpenCode output."""
        lines = output.split("\n")
        for line in lines:
            if line.strip() and not line.startswith("#"):
                parts = line.split(":")
                if len(parts) >= 2:
                    agent = OpenCodeAgent(
                        name=parts[0].strip(),
                        description=parts[1].strip() if len(parts) > 1 else ""
                    )
                    self.available_agents.append(agent)
    
    def execute_opencode_command(
        self,
        command: str,
        args: Optional[List[str]] = None,
        timeout: int = 30
    ) -> Tuple[bool, str]:
        """Execute OpenCode CLI command."""
        try:
            cmd = ["opencode"] + command.split()
            if args:
                cmd.extend(args)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            return success, output
        except subprocess.TimeoutExpired:
            return False, "Command timeout"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def run_with_model(
        self,
        prompt: str,
        model: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """Run prompt with specific OpenCode model."""
        cmd = f'opencode run "{prompt}"'
        if model:
            cmd += f" --model {model}"
        if stream:
            cmd += " --stream"
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def create_opencode_agent(
        self,
        agent_name: str,
        agent_config: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Create new OpenCode agent."""
        try:
            config_file = os.path.join(
                self.opencode_config_dir,
                "agents",
                f"{agent_name}.json"
            )
            
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            with open(config_file, "w") as f:
                json.dump(agent_config, f, indent=2)
            
            return True, f"Agent {agent_name} created successfully"
        except Exception as e:
            return False, f"Failed to create agent: {str(e)}"
    
    def manage_mcp_server(
        self,
        action: str,
        server_name: Optional[str] = None,
        server_config: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """Manage MCP servers."""
        try:
            if action == "list":
                success, output = self.execute_opencode_command("mcp list")
                return success, output
            
            elif action == "add" and server_name and server_config:
                config_file = os.path.join(
                    self.opencode_config_dir,
                    "mcp.json"
                )
                
                # Load existing config
                if os.path.exists(config_file):
                    with open(config_file, "r") as f:
                        config = json.load(f)
                else:
                    config = {"mcpServers": {}}
                
                # Add new server
                config["mcpServers"][server_name] = server_config
                
                # Save config
                with open(config_file, "w") as f:
                    json.dump(config, f, indent=2)
                
                return True, f"MCP server {server_name} added"
            
            elif action == "remove" and server_name:
                config_file = os.path.join(
                    self.opencode_config_dir,
                    "mcp.json"
                )
                
                if os.path.exists(config_file):
                    with open(config_file, "r") as f:
                        config = json.load(f)
                    
                    if server_name in config.get("mcpServers", {}):
                        del config["mcpServers"][server_name]
                        
                        with open(config_file, "w") as f:
                            json.dump(config, f, indent=2)
                        
                        return True, f"MCP server {server_name} removed"
                
                return False, f"MCP server {server_name} not found"
            
            else:
                return False, "Invalid action or missing parameters"
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_session_info(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get session information."""
        try:
            if session_id:
                cmd = f"opencode session info {session_id}"
            else:
                cmd = "opencode session list"
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout,
                    "sessions": self._parse_sessions(result.stdout)
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_sessions(self, output: str) -> List[Dict[str, Any]]:
        """Parse session information."""
        sessions = []
        lines = output.split("\n")
        for line in lines:
            if line.strip() and not line.startswith("#"):
                # Parse session info
                parts = line.split()
                if len(parts) >= 2:
                    sessions.append({
                        "id": parts[0],
                        "name": parts[1] if len(parts) > 1 else "",
                        "timestamp": parts[2] if len(parts) > 2 else ""
                    })
        return sessions
    
    def analyze_and_optimize(self, task: str) -> Dict[str, Any]:
        """Analyze task and suggest optimal OpenCode configuration."""
        if not self.llm_provider:
            return {
                "success": False,
                "error": "LLM provider not available"
            }
        
        system_prompt = self._build_system_prompt()
        
        prompt = f"""Analyze this task and suggest the best OpenCode configuration:

Task: {task}

Available Models: {[m.name for m in self.available_models]}
Available Agents: {[a.name for a in self.available_agents]}

Provide:
1. Best model to use
2. Recommended agent configuration
3. MCP servers that might help
4. Execution strategy

Format as JSON."""
        
        result = self._optimize_and_generate(prompt, system_prompt)
        
        try:
            # Try to parse JSON response
            import re
            json_match = re.search(r'\{.*\}', result['response'], re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return {
                    "success": True,
                    "analysis": analysis,
                    "tokens_saved": result.get('tokens_saved', 0)
                }
        except:
            pass
        
        return {
            "success": True,
            "analysis": result['response'],
            "tokens_saved": result.get('tokens_saved', 0)
        }
    
    def create_multi_agent_workflow(
        self,
        task_description: str,
        num_agents: int = 3
    ) -> Crew:
        """Create multi-agent workflow for OpenCode task."""
        # Create specialized agents
        agents = []
        
        # Planner agent
        planner = LLMAgent(
            name="OpenCode Planner",
            role="Task Planner",
            goal="Plan OpenCode task execution",
            backstory="Expert in OpenCode workflows",
            llm_provider=self.llm_provider,
            agent_type=AgentType.MANAGER
        )
        agents.append(planner)
        
        # Executor agent
        executor = LLMAgent(
            name="OpenCode Executor",
            role="Task Executor",
            goal="Execute OpenCode commands",
            backstory="Expert in OpenCode CLI",
            llm_provider=self.llm_provider,
            agent_type=AgentType.SPECIALIST
        )
        agents.append(executor)
        
        # Reviewer agent
        reviewer = LLMAgent(
            name="OpenCode Reviewer",
            role="Result Reviewer",
            goal="Review execution results",
            backstory="Expert in quality assurance",
            llm_provider=self.llm_provider,
            agent_type=AgentType.SPECIALIST
        )
        agents.append(reviewer)
        
        # Create tasks
        tasks = [
            Task(
                description=f"Plan execution strategy for: {task_description}",
                agent=planner,
                expected_output="Execution plan",
                priority=5
            ),
            Task(
                description=f"Execute: {task_description}",
                agent=executor,
                expected_output="Execution results",
                dependencies=["Plan execution strategy for: " + task_description],
                priority=4
            ),
            Task(
                description="Review and validate results",
                agent=reviewer,
                expected_output="Review report",
                dependencies=["Execute: " + task_description],
                priority=3
            ),
        ]
        
        # Create crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            workflow_type=WorkflowType.SEQUENTIAL,
            project_name=f"OpenCode: {task_description[:50]}"
        )
        
        return crew
    
    def get_opencode_stats(self) -> Dict[str, Any]:
        """Get comprehensive OpenCode statistics."""
        return {
            "available_models": len(self.available_models),
            "available_agents": len(self.available_agents),
            "models": [m.name for m in self.available_models],
            "agents": [a.name for a in self.available_agents],
            "config_dir": self.opencode_config_dir,
            "rlm_stats": self.get_rlm_stats() if self.enable_rlm else {}
        }
    
    def interactive_mode(self):
        """Start interactive OpenCode agent mode."""
        print("=" * 70)
        print("🤖 ADVANCED OPENCODE CLI AGENT - INTERACTIVE MODE")
        print("=" * 70)
        print("\nAvailable commands:")
        print("  1. models - List available models")
        print("  2. agents - List available agents")
        print("  3. run <prompt> - Run prompt")
        print("  4. analyze <task> - Analyze task")
        print("  5. workflow <task> - Create workflow")
        print("  6. stats - Show statistics")
        print("  7. exit - Exit interactive mode")
        print()
        
        while True:
            try:
                user_input = input("OpenCode Agent> ").strip()
                
                if not user_input:
                    continue
                
                if user_input == "exit":
                    print("👋 Goodbye!")
                    break
                
                elif user_input == "models":
                    print(f"\n📊 Available Models ({len(self.available_models)}):")
                    for model in self.available_models:
                        print(f"  • {model.name} ({model.provider})")
                
                elif user_input == "agents":
                    print(f"\n🤖 Available Agents ({len(self.available_agents)}):")
                    for agent in self.available_agents:
                        print(f"  • {agent.name}: {agent.description}")
                
                elif user_input.startswith("run "):
                    prompt = user_input[4:]
                    print(f"\n🚀 Running: {prompt}")
                    result = self.run_with_model(prompt)
                    print(f"\n{result}")
                
                elif user_input.startswith("analyze "):
                    task = user_input[8:]
                    print(f"\n🔍 Analyzing: {task}")
                    analysis = self.analyze_and_optimize(task)
                    print(f"\n{json.dumps(analysis, indent=2)}")
                
                elif user_input.startswith("workflow "):
                    task = user_input[9:]
                    print(f"\n🔄 Creating workflow for: {task}")
                    crew = self.create_multi_agent_workflow(task)
                    print(f"✅ Workflow created with {len(crew.agents)} agents")
                    
                    execute = input("\nExecute workflow? (y/n): ").strip().lower()
                    if execute == "y":
                        crew.kickoff()
                
                elif user_input == "stats":
                    stats = self.get_opencode_stats()
                    print(f"\n📊 OpenCode Statistics:")
                    print(json.dumps(stats, indent=2))
                
                else:
                    print("❌ Unknown command. Type 'exit' to quit.")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
