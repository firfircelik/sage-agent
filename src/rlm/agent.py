"""
RLM-enabled LLM agent with token optimization.
"""

from typing import Optional, Dict, Any
from ..llm import LLMAgent, LLMProvider
from ..core import AgentType, Memory
from .enterprise import EnterpriseRLM


class RLMEnabledLLMAgent(LLMAgent):
    """LLM agent with Enterprise RLM optimization - self-improving AI."""
    
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
        cache_responses: bool = True
    ):
        super().__init__(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            llm_provider=llm_provider,
            agent_type=agent_type,
            memory=memory or Memory(),
            tools=tools or []
        )
        
        self.enable_rlm = enable_rlm
        self.cache_responses = cache_responses
        # Use EnterpriseRLM for full self-improving capabilities
        self.rlm = EnterpriseRLM() if enable_rlm else None
        self.total_tokens_saved = 0
        self.total_requests = 0
        
        if self.rlm:
            self._initialize_rlm_context()
    
    def _initialize_rlm_context(self):
        """Initialize RLM context with agent information."""
        if not self.rlm:
            return
        
        # Add agent info to knowledge base
        agent_id = f"agent_{self.name.lower().replace(' ', '_')}"
        self.rlm.add_knowledge(
            id=agent_id,
            category="agent",
            title=f"Agent: {self.name}",
            content=f"Role: {self.role}\nGoal: {self.goal}\nBackstory: {self.backstory}\nType: {self.agent_type.value}",
            tags=["agent", self.agent_type.value],
            priority=8
        )
    
    def _optimize_and_generate(
        self,
        prompt: str,
        system_prompt: str = ""
    ) -> Dict[str, Any]:
        """Generate response with Enterprise RLM optimization."""
        
        self.total_requests += 1
        
        if not self.enable_rlm or not self.rlm or not self.llm_provider:
            response = self.llm_provider.generate(prompt, system_prompt)
            return {
                "response": response,
                "tokens_saved": 0,
                "from_cache": False,
                "optimization_used": False
            }
        
        # Process with EnterpriseRLM (checks memory, applies advanced optimization)
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        optimization = self.rlm.process_query(
            full_prompt,
            provider=self.llm_provider.__class__.__name__.lower().replace("provider", ""),
            model=getattr(self.llm_provider, 'model', 'unknown'),
            use_intelligence=True,
            validate_response=True,
            use_advanced_optimization=True
        )
        
        # If from memory, return immediately
        if optimization.get("from_memory"):
            self.total_tokens_saved += optimization.get("tokens_saved", 0)
            return {
                "response": optimization["response"],
                "tokens_saved": optimization.get("tokens_saved", 0),
                "from_cache": True,
                "from_memory": True,
                "optimization_used": True,
                "optimization_details": optimization
            }
        
        # Generate new response
        try:
            optimized_prompt = optimization.get("optimized_prompt", prompt)
            context = optimization.get("context_enhanced", "")
            
            if context:
                optimized_prompt += f"\n\nRelevant Context:\n{context}"
            
            response = self.llm_provider.generate(optimized_prompt, system_prompt)
            
            # Remember interaction for learning
            tokens_saved = optimization.get("tokens_saved", 0)
            self.rlm.remember_interaction(
                query=full_prompt,
                response=response,
                context=context,
                provider=self.llm_provider.__class__.__name__.lower().replace("provider", ""),
                model=getattr(self.llm_provider, 'model', 'unknown'),
                tokens_used=optimization.get("estimated_tokens", 0),
                success=True,
                validate=True
            )
            
            self.total_tokens_saved += tokens_saved
            
            return {
                "response": response,
                "tokens_saved": tokens_saved,
                "from_cache": False,
                "from_memory": False,
                "optimization_used": True,
                "optimization_details": optimization
            }
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            # Learn from failure
            if self.rlm:
                self.rlm.remember_interaction(
                    query=full_prompt,
                    response=f"Error: {str(e)}",
                    success=False
                )
            return {
                "response": f"Error: {str(e)}",
                "tokens_saved": 0,
                "from_cache": False,
                "optimization_used": False,
                "error": str(e)
            }
    
    def think(self, task_description: str) -> str:
        """Think about task with RLM optimization."""
        if not self.llm_provider:
            return super().think(task_description)
        
        system_prompt = self._build_system_prompt()
        prompt = f"Analyze and think about this task:\n\n{task_description}"
        
        result = self._optimize_and_generate(prompt, system_prompt)
        
        output = f"💭 {self.name} thinking:\n{result['response']}"
        
        if result["optimization_used"]:
            output += f"\n\n[RLM Optimization] Tokens saved: {result['tokens_saved']}"
        
        return output
    
    def act(self, action: str) -> str:
        """Execute action with RLM optimization."""
        if not self.llm_provider:
            return super().act(action)
        
        system_prompt = self._build_system_prompt()
        prompt = f"Execute this action:\n\n{action}"
        
        result = self._optimize_and_generate(prompt, system_prompt)
        
        output = f"🔧 {self.name} executing:\n{result['response']}"
        
        if result["optimization_used"]:
            output += f"\n\n[RLM Optimization] Tokens saved: {result['tokens_saved']}"
        
        return output
    
    def add_context_to_rlm(self, key: str, content: str, metadata: Dict = None):
        """Add context to RLM knowledge base."""
        if self.rlm:
            self.rlm.add_knowledge(
                id=key,
                category=metadata.get("category", "context") if metadata else "context",
                title=key,
                content=content,
                tags=metadata.get("tags", []) if metadata else [],
                priority=metadata.get("priority", 5) if metadata else 5
            )
    
    def provide_feedback(self, query: str, response: str, feedback: str, rating: int):
        """Provide feedback for self-improvement."""
        if self.rlm:
            self.rlm.provide_feedback(query, response, feedback, rating)
    
    def get_rlm_stats(self) -> Dict[str, Any]:
        """Get comprehensive RLM statistics."""
        if not self.rlm:
            return {}
        
        comprehensive_stats = self.rlm.get_comprehensive_stats()
        
        return {
            "agent_name": self.name,
            "total_requests": self.total_requests,
            "total_tokens_saved": self.total_tokens_saved,
            "average_tokens_saved_per_request": (
                self.total_tokens_saved / self.total_requests
                if self.total_requests > 0 else 0
            ),
            "rlm_enabled": self.enable_rlm,
            "cache_enabled": self.cache_responses,
            "enterprise_stats": comprehensive_stats
        }
    
    def print_rlm_stats(self):
        """Print comprehensive RLM statistics."""
        stats = self.get_rlm_stats()
        
        print(f"\n{'='*60}")
        print(f"🧠 Enterprise RLM Statistics for {stats['agent_name']}")
        print(f"{'='*60}")
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Total Tokens Saved: {stats['total_tokens_saved']}")
        print(f"Avg Tokens Saved/Request: {stats['average_tokens_saved_per_request']:.2f}")
        print(f"RLM Enabled: {stats['rlm_enabled']}")
        print(f"Cache Enabled: {stats['cache_enabled']}")
        
        if stats.get('enterprise_stats'):
            ent = stats['enterprise_stats']
            print(f"\n📊 Enterprise Features:")
            if 'memory' in ent:
                print(f"   Memories: {ent['memory'].get('total_memories', 0)}")
            if 'knowledge_base' in ent:
                print(f"   Knowledge: {ent['knowledge_base'].get('total_entries', 0)}")
            if 'improvement' in ent:
                print(f"   Quality Trend: {ent['improvement'].get('quality_trend', 'N/A')}")
            if 'advanced_optimizer' in ent:
                print(f"   Advanced Optimizations: {ent['advanced_optimizer'].get('total_optimizations', 0)}")
        print(f"{'='*60}")
