"""
Model registry for managing all LLM models.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ModelProvider(Enum):
    """LLM model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    GROQ = "groq"
    COHERE = "cohere"
    MISTRAL = "mistral"


@dataclass
class ModelInfo:
    """Information about an LLM model."""
    name: str
    provider: ModelProvider
    description: str
    context_window: int
    max_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    capabilities: List[str] = field(default_factory=list)
    supported_functions: bool = False
    vision_capable: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_cost_estimate(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for tokens."""
        input_cost = (input_tokens / 1000) * self.cost_per_1k_input
        output_cost = (output_tokens / 1000) * self.cost_per_1k_output
        return input_cost + output_cost


class ModelRegistry:
    """Registry of all available LLM models."""
    
    def __init__(self, auto_discover_opencode: bool = True):
        self.models: Dict[str, ModelInfo] = {}
        self._register_default_models()
        
        if auto_discover_opencode:
            self._discover_opencode_models()
    
    def _register_default_models(self):
        """Register default models."""
        
        # OpenAI Models
        self.register_model(ModelInfo(
            name="gpt-4",
            provider=ModelProvider.OPENAI,
            description="Most capable GPT-4 model",
            context_window=8192,
            max_tokens=4096,
            cost_per_1k_input=0.03,
            cost_per_1k_output=0.06,
            capabilities=["text", "code", "reasoning"],
            supported_functions=True,
            vision_capable=False
        ))
        
        self.register_model(ModelInfo(
            name="gpt-4-turbo",
            provider=ModelProvider.OPENAI,
            description="GPT-4 Turbo with 128K context",
            context_window=128000,
            max_tokens=4096,
            cost_per_1k_input=0.01,
            cost_per_1k_output=0.03,
            capabilities=["text", "code", "reasoning"],
            supported_functions=True,
            vision_capable=True
        ))
        
        self.register_model(ModelInfo(
            name="gpt-3.5-turbo",
            provider=ModelProvider.OPENAI,
            description="Fast and efficient GPT-3.5 Turbo",
            context_window=4096,
            max_tokens=4096,
            cost_per_1k_input=0.0005,
            cost_per_1k_output=0.0015,
            capabilities=["text", "code"],
            supported_functions=True,
            vision_capable=False
        ))
        
        # Anthropic Models
        self.register_model(ModelInfo(
            name="claude-3-opus",
            provider=ModelProvider.ANTHROPIC,
            description="Most capable Claude model",
            context_window=200000,
            max_tokens=4096,
            cost_per_1k_input=0.015,
            cost_per_1k_output=0.075,
            capabilities=["text", "code", "reasoning"],
            supported_functions=True,
            vision_capable=True
        ))
        
        self.register_model(ModelInfo(
            name="claude-3-sonnet",
            provider=ModelProvider.ANTHROPIC,
            description="Balanced Claude model",
            context_window=200000,
            max_tokens=4096,
            cost_per_1k_input=0.003,
            cost_per_1k_output=0.015,
            capabilities=["text", "code"],
            supported_functions=True,
            vision_capable=True
        ))
        
        self.register_model(ModelInfo(
            name="claude-3-haiku",
            provider=ModelProvider.ANTHROPIC,
            description="Fast Claude model",
            context_window=200000,
            max_tokens=4096,
            cost_per_1k_input=0.00025,
            cost_per_1k_output=0.00125,
            capabilities=["text"],
            supported_functions=False,
            vision_capable=True
        ))
        
        # Groq Models
        self.register_model(ModelInfo(
            name="mixtral-8x7b",
            provider=ModelProvider.GROQ,
            description="Fast Mixtral model via Groq",
            context_window=32000,
            max_tokens=4096,
            cost_per_1k_input=0.0,
            cost_per_1k_output=0.0,
            capabilities=["text", "code"],
            supported_functions=False,
            vision_capable=False
        ))
        
        self.register_model(ModelInfo(
            name="llama2-70b",
            provider=ModelProvider.GROQ,
            description="LLaMA 2 70B via Groq",
            context_window=4096,
            max_tokens=4096,
            cost_per_1k_input=0.0,
            cost_per_1k_output=0.0,
            capabilities=["text", "code"],
            supported_functions=False,
            vision_capable=False
        ))
        
        # Cohere Models
        self.register_model(ModelInfo(
            name="command",
            provider=ModelProvider.COHERE,
            description="Cohere Command model",
            context_window=4096,
            max_tokens=4096,
            cost_per_1k_input=0.001,
            cost_per_1k_output=0.002,
            capabilities=["text"],
            supported_functions=False,
            vision_capable=False
        ))
        
        # Mistral Models
        self.register_model(ModelInfo(
            name="mistral-7b",
            provider=ModelProvider.MISTRAL,
            description="Mistral 7B model",
            context_window=8000,
            max_tokens=4096,
            cost_per_1k_input=0.00014,
            cost_per_1k_output=0.00042,
            capabilities=["text", "code"],
            supported_functions=False,
            vision_capable=False
        ))
        
        # Local Models
        self.register_model(ModelInfo(
            name="llama2",
            provider=ModelProvider.LOCAL,
            description="LLaMA 2 local model",
            context_window=4096,
            max_tokens=4096,
            cost_per_1k_input=0.0,
            cost_per_1k_output=0.0,
            capabilities=["text", "code"],
            supported_functions=False,
            vision_capable=False
        ))
        
        # DeepSeek Models
        self.register_model(ModelInfo(
            name="deepseek-chat",
            provider=ModelProvider.OPENAI,
            description="DeepSeek Chat model",
            context_window=4096,
            max_tokens=4096,
            cost_per_1k_input=0.0001,
            cost_per_1k_output=0.0002,
            capabilities=["text", "code", "reasoning"],
            supported_functions=True,
            vision_capable=False
        ))
        
        self.register_model(ModelInfo(
            name="deepseek-coder",
            provider=ModelProvider.OPENAI,
            description="DeepSeek Coder model",
            context_window=4096,
            max_tokens=4096,
            cost_per_1k_input=0.0001,
            cost_per_1k_output=0.0002,
            capabilities=["text", "code"],
            supported_functions=True,
            vision_capable=False
        ))
        
        # GLM (Zhipu) Models
        self.register_model(ModelInfo(
            name="glm-4",
            provider=ModelProvider.OPENAI,
            description="Zhipu GLM-4 model",
            context_window=8192,
            max_tokens=4096,
            cost_per_1k_input=0.0001,
            cost_per_1k_output=0.0002,
            capabilities=["text", "code", "reasoning"],
            supported_functions=True,
            vision_capable=True
        ))
        
        self.register_model(ModelInfo(
            name="glm-3-turbo",
            provider=ModelProvider.OPENAI,
            description="Zhipu GLM-3 Turbo model",
            context_window=4096,
            max_tokens=4096,
            cost_per_1k_input=0.00005,
            cost_per_1k_output=0.00008,
            capabilities=["text", "code"],
            supported_functions=False,
            vision_capable=False
        ))
    
    def register_model(self, model: ModelInfo):
        """Register a model."""
        self.models[model.name] = model
    
    def get_model(self, name: str) -> Optional[ModelInfo]:
        """Get model by name."""
        return self.models.get(name)
    
    def list_models(self, provider: Optional[ModelProvider] = None) -> List[ModelInfo]:
        """List models."""
        if provider:
            return [m for m in self.models.values() if m.provider == provider]
        return list(self.models.values())
    
    def list_models_by_provider(self) -> Dict[ModelProvider, List[ModelInfo]]:
        """List models grouped by provider."""
        result = {}
        for model in self.models.values():
            if model.provider not in result:
                result[model.provider] = []
            result[model.provider].append(model)
        return result
    
    def get_cheapest_model(self) -> Optional[ModelInfo]:
        """Get cheapest model."""
        if not self.models:
            return None
        return min(
            self.models.values(),
            key=lambda m: m.cost_per_1k_input + m.cost_per_1k_output
        )
    
    def get_most_capable_model(self) -> Optional[ModelInfo]:
        """Get most capable model."""
        if not self.models:
            return None
        return max(
            self.models.values(),
            key=lambda m: len(m.capabilities)
        )
    
    def _discover_opencode_models(self):
        """Discover models from OpenCode CLI."""
        try:
            import subprocess
            result = subprocess.run(
                ["opencode", "models"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                self._parse_opencode_models(result.stdout)
        except Exception as e:
            # Silently fail if OpenCode not available
            pass
    
    def _parse_opencode_models(self, output: str):
        """Parse OpenCode models output."""
        lines = output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('Model'):
                continue
            
            # Parse format: "model-name    provider    status"
            parts = line.split()
            if len(parts) >= 2:
                model_name = parts[0]
                provider_name = parts[1] if len(parts) > 1 else "opencode"
                
                # Skip if already registered
                if model_name in self.models:
                    continue
                
                # Map provider name to enum
                provider = self._map_provider(provider_name)
                
                # Register model
                self.register_model(ModelInfo(
                    name=model_name,
                    provider=provider,
                    description=f"OpenCode model: {model_name}",
                    context_window=8192,  # Default
                    max_tokens=4096,
                    cost_per_1k_input=0.0,  # Unknown
                    cost_per_1k_output=0.0,
                    capabilities=["text", "code"],
                    supported_functions=False,
                    vision_capable=False,
                    metadata={"source": "opencode", "provider": provider_name}
                ))
    
    def _map_provider(self, provider_name: str) -> ModelProvider:
        """Map provider name to enum."""
        provider_map = {
            "openai": ModelProvider.OPENAI,
            "anthropic": ModelProvider.ANTHROPIC,
            "groq": ModelProvider.GROQ,
            "cohere": ModelProvider.COHERE,
            "mistral": ModelProvider.MISTRAL,
            "local": ModelProvider.LOCAL,
        }
        return provider_map.get(provider_name.lower(), ModelProvider.OPENAI)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        models_by_provider = self.list_models_by_provider()
        
        # Count OpenCode-discovered models
        opencode_models = [
            m for m in self.models.values() 
            if m.metadata.get("source") == "opencode"
        ]
        
        return {
            "total_models": len(self.models),
            "opencode_discovered": len(opencode_models),
            "providers": {
                provider.value: len(models)
                for provider, models in models_by_provider.items()
            },
            "models": [m.name for m in self.models.values()]
        }
