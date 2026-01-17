"""
MCP (Model Context Protocol) server management with built-in registry.
"""

import json
import os
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime
from .mcp_registry import MCPRegistry, MCPServerTemplate


@dataclass
class MCPServer:
    """MCP Server configuration."""
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    disabled: bool = False
    auto_approve: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    source: str = "custom"  # custom or registry
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "command": self.command,
            "args": self.args,
            "env": self.env,
            "disabled": self.disabled,
            "autoApprove": self.auto_approve
        }


class MCPManager:
    """Manage MCP servers with built-in registry."""
    
    def __init__(self, config_dir: str = ".mcp_config"):
        self.config_dir = os.path.expanduser(config_dir)
        self.config_file = os.path.join(self.config_dir, "mcp.json")
        self.servers: Dict[str, MCPServer] = {}
        self.registry = MCPRegistry()
        self._load_config()
    
    def _load_config(self):
        """Load MCP configuration from file."""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, "r") as f:
                data = json.load(f)
                for name, config in data.get("mcpServers", {}).items():
                    self.servers[name] = MCPServer(
                        name=name,
                        command=config.get("command", ""),
                        args=config.get("args", []),
                        env=config.get("env", {}),
                        disabled=config.get("disabled", False),
                        auto_approve=config.get("autoApprove", []),
                        source=config.get("source", "custom")
                    )
        except Exception as e:
            print(f"⚠️  Failed to load MCP config: {e}")
    
    def _save_config(self):
        """Save MCP configuration to file."""
        os.makedirs(self.config_dir, exist_ok=True)
        
        try:
            data = {
                "mcpServers": {
                    name: {
                        **server.to_dict(),
                        "source": server.source
                    }
                    for name, server in self.servers.items()
                }
            }
            with open(self.config_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save MCP config: {e}")
    
    def add_from_registry(
        self,
        template_name: str,
        custom_name: Optional[str] = None,
        env_overrides: Optional[Dict[str, str]] = None
    ) -> Optional[MCPServer]:
        """Add server from built-in registry."""
        template = self.registry.get(template_name)
        if not template:
            print(f"❌ Template '{template_name}' not found in registry")
            return None
        
        name = custom_name or template.name
        
        # Merge environment variables
        env = template.env.copy()
        if env_overrides:
            env.update(env_overrides)
        
        server = MCPServer(
            name=name,
            command=template.command,
            args=template.args.copy(),
            env=env,
            auto_approve=template.auto_approve.copy() if template.auto_approve else [],
            source="registry"
        )
        
        self.servers[name] = server
        self._save_config()
        
        print(f"✅ Added MCP server '{name}' from registry")
        return server
    
    def add_server(
        self,
        name: str,
        command: str,
        args: List[str] = None,
        env: Dict[str, str] = None,
        auto_approve: List[str] = None
    ) -> MCPServer:
        """Add custom MCP server."""
        server = MCPServer(
            name=name,
            command=command,
            args=args or [],
            env=env or {},
            auto_approve=auto_approve or [],
            source="custom"
        )
        self.servers[name] = server
        self._save_config()
        return server
    
    def remove_server(self, name: str) -> bool:
        """Remove MCP server."""
        if name in self.servers:
            del self.servers[name]
            self._save_config()
            return True
        return False
    
    def enable_server(self, name: str) -> bool:
        """Enable MCP server."""
        if name in self.servers:
            self.servers[name].disabled = False
            self._save_config()
            return True
        return False
    
    def disable_server(self, name: str) -> bool:
        """Disable MCP server."""
        if name in self.servers:
            self.servers[name].disabled = True
            self._save_config()
            return True
        return False
    
    def get_server(self, name: str) -> Optional[MCPServer]:
        """Get MCP server."""
        return self.servers.get(name)
    
    def list_servers(self) -> List[MCPServer]:
        """List all MCP servers."""
        return list(self.servers.values())
    
    def list_enabled_servers(self) -> List[MCPServer]:
        """List enabled MCP servers."""
        return [s for s in self.servers.values() if not s.disabled]
    
    def list_registry_servers(self) -> List[MCPServerTemplate]:
        """List available servers in registry."""
        return self.registry.list_all()
    
    def search_registry(self, query: str) -> List[MCPServerTemplate]:
        """Search registry."""
        return self.registry.search(query)
    
    def get_registry_categories(self) -> List[str]:
        """Get registry categories."""
        return self.registry.get_categories()
    
    def list_registry_by_category(self, category: str) -> List[MCPServerTemplate]:
        """List registry servers by category."""
        return self.registry.list_by_category(category)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get MCP statistics."""
        registry_stats = self.registry.get_stats()
        
        return {
            "installed_servers": len(self.servers),
            "enabled_servers": len(self.list_enabled_servers()),
            "disabled_servers": len([s for s in self.servers.values() if s.disabled]),
            "from_registry": len([s for s in self.servers.values() if s.source == "registry"]),
            "custom_servers": len([s for s in self.servers.values() if s.source == "custom"]),
            "registry_available": registry_stats["total_servers"],
            "registry_categories": len(registry_stats["categories"]),
            "servers": [s.name for s in self.servers.values()]
        }
