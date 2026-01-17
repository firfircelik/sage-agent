"""
LLM provider implementations for OpenAI, Anthropic, Groq, Cohere, Mistral, and local models.
"""

import os
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text from prompt."""
        pass

    @abstractmethod
    def chat(self, messages: list) -> str:
        """Chat with the model."""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI library not installed. Install with: pip install openai"
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text using OpenAI."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ OpenAI Error: {e}")
            return f"[OpenAI Error: {str(e)}]"

    def chat(self, messages: list) -> str:
        """Chat with OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ OpenAI Chat Error: {e}")
            return f"[OpenAI Error: {str(e)}]"

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {"provider": "openai", "model": self.model, "type": "chat_completion"}


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"
    ):
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "Anthropic library not installed. Install with: pip install anthropic"
            )

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text using Claude."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt or "You are a helpful AI assistant.",
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except Exception as e:
            print(f"❌ Claude Error: {e}")
            return f"[Claude Error: {str(e)}]"

    def chat(self, messages: list) -> str:
        """Chat with Claude."""
        try:
            response = self.client.messages.create(
                model=self.model, max_tokens=2000, messages=messages
            )
            return response.content[0].text
        except Exception as e:
            print(f"❌ Claude Chat Error: {e}")
            return f"[Claude Error: {str(e)}]"

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {"provider": "anthropic", "model": self.model, "type": "chat_completion"}


class LocalLLMProvider(LLMProvider):
    """Local LLM provider (Ollama, LLaMA, etc.)."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        try:
            import requests
        except ImportError:
            raise ImportError(
                "requests library not installed. Install with: pip install requests"
            )

        self.base_url = base_url
        self.model = model
        self.requests = requests

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text using local LLM."""
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": full_prompt, "stream": False},
            )

            if response.status_code == 200:
                return response.json()["response"]
            else:
                return f"[Local LLM Error: {response.status_code}]"
        except Exception as e:
            print(f"❌ Local LLM Error: {e}")
            return f"[Local LLM Error: {str(e)}]"

    def chat(self, messages: list) -> str:
        """Chat with local LLM."""
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        return self.generate(prompt)

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "provider": "local",
            "model": self.model,
            "base_url": self.base_url,
            "type": "local_completion",
        }


class GroqProvider(LLMProvider):
    """Groq API provider for fast inference."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "mixtral-8x7b-32768"
    ):
        try:
            from groq import Groq
        except ImportError:
            raise ImportError(
                "Groq library not installed. Install with: pip install groq"
            )

        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        self.client = Groq(api_key=self.api_key)
        self.model = model

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text using Groq."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Groq Error: {e}")
            return f"[Groq Error: {str(e)}]"

    def chat(self, messages: list) -> str:
        """Chat with Groq."""
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Groq Chat Error: {e}")
            return f"[Groq Error: {str(e)}]"

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {"provider": "groq", "model": self.model, "type": "chat_completion"}


class CohereProvider(LLMProvider):
    """Cohere API provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "command"):
        try:
            import cohere
        except ImportError:
            raise ImportError(
                "Cohere library not installed. Install with: pip install cohere"
            )

        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError("COHERE_API_KEY environment variable not set")

        self.client = cohere.ClientV2(api_key=self.api_key)
        self.model = model

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text using Cohere."""
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            response = self.client.chat(
                model=self.model, messages=[{"role": "user", "content": full_prompt}]
            )
            return response.message.content[0].text
        except Exception as e:
            print(f"❌ Cohere Error: {e}")
            return f"[Cohere Error: {str(e)}]"

    def chat(self, messages: list) -> str:
        """Chat with Cohere."""
        try:
            response = self.client.chat(model=self.model, messages=messages)
            return response.message.content[0].text
        except Exception as e:
            print(f"❌ Cohere Chat Error: {e}")
            return f"[Cohere Error: {str(e)}]"

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {"provider": "cohere", "model": self.model, "type": "chat_completion"}


class MistralProvider(LLMProvider):
    """Mistral API provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "mistral-small"):
        try:
            from mistralai.client import MistralClient
        except ImportError:
            raise ImportError(
                "Mistral library not installed. Install with: pip install mistralai"
            )

        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY environment variable not set")

        self.client = MistralClient(api_key=self.api_key)
        self.model = model

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text using Mistral."""
        try:
            from mistralai.models.chat_message import ChatMessage

            messages = []
            if system_prompt:
                messages.append(ChatMessage(role="system", content=system_prompt))
            messages.append(ChatMessage(role="user", content=prompt))

            response = self.client.chat(
                model=self.model, messages=messages, temperature=0.7, max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Mistral Error: {e}")
            return f"[Mistral Error: {str(e)}]"

    def chat(self, messages: list) -> str:
        """Chat with Mistral."""
        try:
            from mistralai.models.chat_message import ChatMessage

            mistral_messages = [
                ChatMessage(role=m["role"], content=m["content"]) for m in messages
            ]

            response = self.client.chat(
                model=self.model,
                messages=mistral_messages,
                temperature=0.7,
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Mistral Chat Error: {e}")
            return f"[Mistral Error: {str(e)}]"

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {"provider": "mistral", "model": self.model, "type": "chat_completion"}


class DeepSeekProvider(LLMProvider):
    """DeepSeek API provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI library not installed. Install with: pip install openai"
            )

        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")

        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        self.model = model

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text using DeepSeek."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ DeepSeek Error: {e}")
            return f"[DeepSeek Error: {str(e)}]"

    def chat(self, messages: list) -> str:
        """Chat with DeepSeek."""
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ DeepSeek Chat Error: {e}")
            return f"[DeepSeek Error: {str(e)}]"

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {"provider": "deepseek", "model": self.model, "type": "chat_completion"}


class GLMProvider(LLMProvider):
    """Zhipu GLM API provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "glm-4"):
        try:
            import zhipuai
        except ImportError:
            raise ImportError(
                "Zhipu library not installed. Install with: pip install zhipuai"
            )

        self.api_key = api_key or os.getenv("GLM_API_KEY")
        if not self.api_key:
            raise ValueError("GLM_API_KEY environment variable not set")

        zhipuai.api_key = self.api_key
        self.model = model

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text using GLM."""
        try:
            import zhipuai

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = zhipuai.model_api.invoke(
                model=self.model, messages=messages, temperature=0.7, max_tokens=2000
            )
            return response.get("choices", [{}])[0].get("content", "")
        except Exception as e:
            print(f"❌ GLM Error: {e}")
            return f"[GLM Error: {str(e)}]"

    def chat(self, messages: list) -> str:
        """Chat with GLM."""
        try:
            import zhipuai

            response = zhipuai.model_api.invoke(
                model=self.model, messages=messages, temperature=0.7, max_tokens=2000
            )
            return response.get("choices", [{}])[0].get("content", "")
        except Exception as e:
            print(f"❌ GLM Chat Error: {e}")
            return f"[GLM Error: {str(e)}]"

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {"provider": "glm", "model": self.model, "type": "chat_completion"}


class OpenCodeProvider(LLMProvider):
    """OpenCode integrated provider for accessing all OpenCode models."""

    def __init__(self, model: str = "auto"):
        self.model = model
        self.available_models = []
        self._load_opencode_models()
        self._update_model_registry()

    def _load_opencode_models(self):
        """Load available models from OpenCode."""
        try:
            import subprocess  # nosec B404

            result = subprocess.run(
                ["opencode", "models"],
                capture_output=True,
                text=True,
                timeout=10,
            )  # nosec
            if result.returncode == 0:
                # Parse models from output
                lines = result.stdout.split("\n")
                for line in lines:
                    line = line.strip()
                    if (
                        line
                        and not line.startswith("#")
                        and not line.startswith("Model")
                    ):
                        parts = line.split()
                        if parts:
                            self.available_models.append(parts[0])
        except Exception as e:
            print(f"⚠️  Could not load OpenCode models: {e}")

    def _update_model_registry(self):
        """Update ModelRegistry with discovered models."""
        if not self.available_models:
            return

        try:
            import subprocess  # nosec B404

            result = subprocess.run(
                ["opencode", "models"],
                capture_output=True,
                text=True,
                timeout=10,
            )  # nosec
            if result.returncode == 0:
                # Import here to avoid circular dependency
                import sys
                import os

                sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
                from utils.model_registry import ModelRegistry

                registry = ModelRegistry(auto_discover_opencode=False)
                registry._parse_opencode_models(result.stdout)
        except Exception:
            return

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text using OpenCode."""
        try:
            import subprocess  # nosec B404

            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            cmd = ["opencode", "run", full_prompt]
            if self.model != "auto":
                cmd += ["--model", self.model]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )  # nosec

            if result.returncode == 0:
                return result.stdout
            else:
                return f"[OpenCode Error: {result.stderr}]"
        except Exception as e:
            print(f"❌ OpenCode Error: {e}")
            return f"[OpenCode Error: {str(e)}]"

    def chat(self, messages: list) -> str:
        """Chat with OpenCode."""
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        return self.generate(prompt)

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "provider": "opencode",
            "model": self.model,
            "type": "integrated",
            "available_models": self.available_models,
        }


class LLMFactory:
    """Factory for creating LLM providers."""

    _providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "claude": AnthropicProvider,
        "local": LocalLLMProvider,
        "ollama": LocalLLMProvider,
        "groq": GroqProvider,
        "cohere": CohereProvider,
        "mistral": MistralProvider,
        "deepseek": DeepSeekProvider,
        "glm": GLMProvider,
        "zhipu": GLMProvider,
        "opencode": OpenCodeProvider,
    }

    @staticmethod
    def create(provider: str = "openai", **kwargs) -> LLMProvider:
        """Create an LLM provider instance."""
        provider_lower = provider.lower()

        if provider_lower not in LLMFactory._providers:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Supported: {list(LLMFactory._providers.keys())}"
            )

        provider_class = LLMFactory._providers[provider_lower]
        return provider_class(**kwargs)

    @staticmethod
    def get_default() -> Optional[LLMProvider]:
        """Get default LLM provider from environment."""
        provider = os.getenv("LLM_PROVIDER", "openai").lower()

        try:
            return LLMFactory.create(provider)
        except Exception as e:
            print(f"⚠️  Failed to load default LLM ({provider}): {e}")
            print(
                "💡 Tip: Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable"
            )
            return None

    @staticmethod
    def list_providers() -> List[str]:
        """List available providers."""
        return list(LLMFactory._providers.keys())
