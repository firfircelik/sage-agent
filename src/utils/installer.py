"""
Installer utilities for OpenCode CLI and Claude Code CLI integration.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, Optional, Tuple


def _load_json(path: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not os.path.exists(path):
        return default or {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default or {}


def _save_json(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _expand(path: str) -> str:
    return os.path.expanduser(path)


def get_opencode_config_path() -> str:
    return _expand("~/.config/opencode/opencode.json")


def get_claude_desktop_config_path() -> str:
    if sys.platform == "darwin":
        return _expand(
            "~/Library/Application Support/Claude/claude_desktop_config.json"
        )
    if sys.platform.startswith("linux"):
        return _expand("~/.config/Claude/claude_desktop_config.json")
    return _expand("~/.claude/claude_desktop_config.json")


def install_opencode_plugin(plugin_name: str = "sage-agent") -> Tuple[bool, str]:
    config_path = get_opencode_config_path()
    config = _load_json(config_path, default={})

    plugins = config.get("plugin")
    if plugins is None:
        plugins = []
    if plugin_name not in plugins:
        plugins.append(plugin_name)
    config["plugin"] = plugins

    # Keep compatibility with alternate key if present
    alt_plugins = config.get("plugins")
    if isinstance(alt_plugins, list):
        if plugin_name not in alt_plugins:
            alt_plugins.append(plugin_name)
        config["plugins"] = alt_plugins

    _save_json(config_path, config)
    return True, f"OpenCode plugin registered in {config_path}"


def uninstall_opencode_plugin(plugin_name: str = "sage-agent") -> Tuple[bool, str]:
    config_path = get_opencode_config_path()
    config = _load_json(config_path, default={})

    changed = False
    plugins = config.get("plugin")
    if isinstance(plugins, list) and plugin_name in plugins:
        plugins = [p for p in plugins if p != plugin_name]
        config["plugin"] = plugins
        changed = True

    alt_plugins = config.get("plugins")
    if isinstance(alt_plugins, list) and plugin_name in alt_plugins:
        alt_plugins = [p for p in alt_plugins if p != plugin_name]
        config["plugins"] = alt_plugins
        changed = True

    if changed:
        _save_json(config_path, config)
        return True, f"OpenCode plugin removed from {config_path}"

    return False, "OpenCode plugin not found"


def install_claude_mcp(
    mcp_name: str = "sage-agent", python_path: Optional[str] = None
) -> Tuple[bool, str]:
    config_path = get_claude_desktop_config_path()
    config = _load_json(config_path, default={"mcpServers": {}})

    if "mcpServers" not in config:
        config["mcpServers"] = {}

    python_executable = python_path or sys.executable
    server_entry = {
        "command": python_executable,
        "args": [os.path.abspath("mcp_server.py")],
        "env": {
            "OPENAI_API_KEY": "",
            "ANTHROPIC_API_KEY": "",
            "DEEPSEEK_API_KEY": "",
            "GLM_API_KEY": "",
        },
    }

    config["mcpServers"][mcp_name] = server_entry
    _save_json(config_path, config)
    return True, f"Claude MCP registered in {config_path}"


def uninstall_claude_mcp(mcp_name: str = "sage-agent") -> Tuple[bool, str]:
    config_path = get_claude_desktop_config_path()
    config = _load_json(config_path, default={"mcpServers": {}})

    if mcp_name in config.get("mcpServers", {}):
        del config["mcpServers"][mcp_name]
        _save_json(config_path, config)
        return True, f"Claude MCP removed from {config_path}"

    return False, "Claude MCP not found"


def doctor() -> Dict[str, Any]:
    opencode_path = get_opencode_config_path()
    claude_path = get_claude_desktop_config_path()

    opencode_config = _load_json(opencode_path, default={})
    claude_config = _load_json(claude_path, default={})

    opencode_plugins = (
        opencode_config.get("plugin") or opencode_config.get("plugins") or []
    )
    claude_mcps = claude_config.get("mcpServers", {})

    return {
        "opencode_config_path": opencode_path,
        "opencode_plugin_registered": "sage-agent" in opencode_plugins,
        "claude_config_path": claude_path,
        "claude_mcp_registered": "sage-agent" in claude_mcps,
        "python_executable": sys.executable,
    }
