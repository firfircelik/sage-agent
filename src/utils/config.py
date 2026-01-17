"""
Configuration management for Sage Agent system.
"""

import os
import json
from typing import Dict, Any

try:
    import yaml
except ImportError:
    yaml = None


class ConfigManager:
    """Manage system configuration."""

    def __init__(self, config_file: str = "config/config.yaml"):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from file."""
        if not os.path.exists(self.config_file):
            self.config = self._get_default_config()
            return

        try:
            with open(self.config_file, "r") as f:
                if self.config_file.endswith(".yaml") or self.config_file.endswith(
                    ".yml"
                ):
                    if yaml is None:
                        print("⚠️  PyYAML not installed. Using JSON fallback.")
                        self.config = self._get_default_config()
                    else:
                        self.config = yaml.safe_load(f) or {}
                elif self.config_file.endswith(".json"):
                    self.config = json.load(f)
        except Exception as e:
            print(f"⚠️  Failed to load config: {e}")
            self.config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "system": {"name": "Sage Agent", "verbose": True, "debug": False},
            "llm": {
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            "rlm": {
                "enabled": True,
                "cache_responses": True,
                "cache_dir": ".rlm_cache",
                "max_context_length": 2000,
                "context_top_k": 3,
            },
            "agents": {
                "default_type": "specialist",
                "enable_memory": True,
                "enable_tools": True,
            },
            "workflow": {"type": "sequential", "verbose": True, "timeout": 300},
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "logs/sage_agent.log",
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self):
        """Save configuration to file."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

        try:
            with open(self.config_file, "w") as f:
                if self.config_file.endswith(".yaml") or self.config_file.endswith(
                    ".yml"
                ):
                    if yaml is None:
                        print("⚠️  PyYAML not installed. Saving as JSON instead.")
                        json.dump(self.config, f, indent=2)
                    else:
                        yaml.dump(self.config, f, default_flow_style=False)
                elif self.config_file.endswith(".json"):
                    json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save config: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return self.config.copy()
