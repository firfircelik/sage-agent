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
    config = _load_json(config_path, default={"plugin": []})

    # Get the absolute path to the TypeScript plugin directory (only this one!)
    opencode_plugin_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "opencode-plugin")
    )
    opencode_plugin_manifest = os.path.join(opencode_plugin_dir, "package.json")

    # Verify plugin manifest exists
    if not os.path.exists(opencode_plugin_manifest):
        return False, f"OpenCode plugin package.json not found at {opencode_plugin_manifest}"

    plugins = config.get("plugin", [])
    
    # Remove old sage-agent entries (plugin name and old paths)
    old_plugin_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "plugin")
    )
    plugins = [
        p for p in plugins 
        if p not in (plugin_name, old_plugin_dir, opencode_plugin_dir)
    ]

    # Add only the TypeScript plugin directory
    plugins.append(opencode_plugin_dir)

    config["plugin"] = plugins

    _save_json(config_path, config)
    return True, f"OpenCode plugin registered in {config_path}"


def uninstall_opencode_plugin(plugin_name: str = "sage-agent") -> Tuple[bool, str]:
    config_path = get_opencode_config_path()
    config = _load_json(config_path, default={})

    # Get the absolute path to the TypeScript plugin directory
    opencode_plugin_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "opencode-plugin")
    )

    changed = False
    plugins = config.get("plugin")
    if isinstance(plugins, list):
        original_len = len(plugins)
        plugins = [p for p in plugins if p != opencode_plugin_dir]
        if len(plugins) < original_len:
            config["plugin"] = plugins
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

    # Get absolute paths
    python_executable = python_path or sys.executable
    mcp_server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "mcp_server.py"))
    project_dir = os.path.dirname(mcp_server_path)
    
    # Verify MCP server exists
    if not os.path.exists(mcp_server_path):
        return False, f"MCP server not found at {mcp_server_path}"
    
    server_entry = {
        "command": python_executable,
        "args": [mcp_server_path],
        "cwd": project_dir,
        "env": {
            "OPENAI_API_KEY": "",
            "ANTHROPIC_API_KEY": "",
            "DEEPSEEK_API_KEY": "",
            "GLM_API_KEY": "",
        },
    }

    config["mcpServers"][mcp_name] = server_entry
    _save_json(config_path, config)
    return True, f"Claude MCP registered in {config_path}\n  Server: {mcp_server_path}\n  Python: {python_executable}"


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

    opencode_plugins = opencode_config.get("plugin") or []
    claude_mcps = claude_config.get("mcpServers", {})

    # Get the TypeScript plugin directory path
    opencode_plugin_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "opencode-plugin")
    )

    # Check if plugin is registered
    opencode_registered = (
        opencode_plugin_dir in opencode_plugins
        or any(opencode_plugin_dir in str(p) for p in opencode_plugins)
    )

    return {
        "opencode_config_path": opencode_path,
        "opencode_config_exists": os.path.exists(opencode_path),
        "opencode_plugin_registered": opencode_registered,
        "opencode_ts_plugin_dir": opencode_plugin_dir,
        "claude_config_path": claude_path,
        "claude_config_exists": os.path.exists(claude_path),
        "claude_mcp_registered": "sage-agent" in claude_mcps,
        "python_executable": sys.executable,
    }
