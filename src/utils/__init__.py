"""
Utility module for Sage Agent system.
"""

from .config import ConfigManager
from .logger import setup_logger, get_logger
from .model_registry import ModelRegistry, ModelInfo
from .validators import validate_prompt, validate_agent_config
from .installer import (
    install_opencode_plugin,
    uninstall_opencode_plugin,
    install_claude_mcp,
    uninstall_claude_mcp,
    doctor,
)

__all__ = [
    "ConfigManager",
    "setup_logger",
    "get_logger",
    "ModelRegistry",
    "ModelInfo",
    "validate_prompt",
    "validate_agent_config",
    "install_opencode_plugin",
    "uninstall_opencode_plugin",
    "install_claude_mcp",
    "uninstall_claude_mcp",
    "doctor",
]
