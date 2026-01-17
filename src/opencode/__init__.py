"""
OpenCode CLI integration module for Sage Agent system.
"""

from .cli_agent import OpenCodeCLIAgent, OpenCodeCommand
from .advanced_cli_agent import AdvancedOpenCodeCLIAgent, OpenCodeModel, OpenCodeAgent
from .mcp_manager import MCPManager, MCPServer
from .session_manager import SessionManager, SessionInfo
from .plugin import register as register_plugin, unregister as unregister_plugin

__all__ = [
    "OpenCodeCLIAgent",
    "OpenCodeCommand",
    "AdvancedOpenCodeCLIAgent",
    "OpenCodeModel",
    "OpenCodeAgent",
    "MCPManager",
    "MCPServer",
    "SessionManager",
    "SessionInfo",
    "register_plugin",
    "unregister_plugin",
]
