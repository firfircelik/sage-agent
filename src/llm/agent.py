"""
LLM-powered agent with real language model capabilities.
"""

from typing import Optional
from ..core import Agent, AgentType, Memory
from .providers import LLMProvider


class LLMAgent(Agent):
    """Agent with LLM capabilities."""

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
            agent_type=agent_type,
            memory=memory or Memory(),
            tools=tools or [],
        )
        self.llm_provider = llm_provider

    def _build_system_prompt(self) -> str:
        """Build system prompt from agent properties."""
        return f"""You are {self.name}, a {self.role}.

Your goal: {self.goal}

Background: {self.backstory}

You are part of the Sage Agent team working together to solve problems.
Provide clear, actionable responses."""

    def think(self, task_description: str) -> str:
        """Think about a task using LLM."""
        if not self.llm_provider:
            return super().think(task_description)

        system_prompt = self._build_system_prompt()
        prompt = f"Analyze and think about this task:\n\n{task_description}"

        response = self.llm_provider.generate(prompt, system_prompt)
        return f"💭 {self.name} thinking:\n{response}"

    def act(self, action: str) -> str:
        """Execute an action using LLM."""
        if not self.llm_provider:
            return super().act(action)

        system_prompt = self._build_system_prompt()
        prompt = f"Execute this action:\n\n{action}"

        response = self.llm_provider.generate(prompt, system_prompt)
        return f"🔧 {self.name} executing:\n{response}"

    def analyze(self, content: str) -> str:
        """Analyze content using LLM."""
        if not self.llm_provider:
            return f"{self.name} analyzing: {content[:50]}..."

        system_prompt = self._build_system_prompt()
        prompt = f"Analyze this content:\n\n{content}"

        return self.llm_provider.generate(prompt, system_prompt)

    def review_code(self, code: str) -> str:
        """Review code using LLM."""
        if not self.llm_provider:
            return f"{self.name} reviewing code..."

        system_prompt = self._build_system_prompt()
        prompt = f"""Review this code and provide feedback:

```
{code}
```

Check for:
1. Code quality
2. Security issues
3. Performance improvements
4. Best practices"""

        return self.llm_provider.generate(prompt, system_prompt)

    def generate_documentation(self, code: str, title: str = "") -> str:
        """Generate documentation using LLM."""
        if not self.llm_provider:
            return f"{self.name} generating documentation..."

        system_prompt = self._build_system_prompt()
        prompt = f"""Generate documentation for this code:

```
{code}
```

Title: {title}

Include:
1. Overview
2. Parameters
3. Return values
4. Usage examples
5. Notes"""

        return self.llm_provider.generate(prompt, system_prompt)
