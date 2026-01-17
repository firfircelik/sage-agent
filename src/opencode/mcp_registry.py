"""
Built-in MCP Server Registry - User manages their own MCP servers.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import os


@dataclass
class MCPServerTemplate:
    """MCP Server template."""
    name: str
    description: str
    command: str
    args: List[str]
    env: Dict[str, str]
    category: str
    requires_api_key: bool = False
    api_key_env: str = ""
    auto_approve: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "command": self.command,
            "args": self.args,
            "env": self.env,
            "category": self.category,
            "requires_api_key": self.requires_api_key,
            "api_key_env": self.api_key_env,
            "auto_approve": self.auto_approve or []
        }


class MCPRegistry:
    """User-managed MCP server registry."""
    
    def __init__(self, storage_dir: str = ".mcp_config"):
        self.storage_dir = os.path.expanduser(storage_dir)
        self.registry_file = os.path.join(self.storage_dir, "registry.json")
        self.servers: Dict[str, MCPServerTemplate] = {}
        self._load()
    
    def register(self, server: MCPServerTemplate) -> bool:
        """Register MCP server template."""
        try:
            self.servers[server.name] = server
            self._save()
            return True
        except Exception as e:
            print(f"❌ Failed to register server: {e}")
            return False
    
    def unregister(self, name: str) -> bool:
        """Unregister MCP server template."""
        if name in self.servers:
            del self.servers[name]
            self._save()
            return True
        return False
    
    def get(self, name: str) -> Optional[MCPServerTemplate]:
        """Get server template by name."""
        return self.servers.get(name)
    
    def list_all(self) -> List[MCPServerTemplate]:
        """List all server templates."""
        return list(self.servers.values())
    
    def list_by_category(self, category: str) -> List[MCPServerTemplate]:
        """List servers by category."""
        return [s for s in self.servers.values() if s.category == category]
    
    def get_categories(self) -> List[str]:
        """Get all categories."""
        return list(set(s.category for s in self.servers.values()))
    
    def search(self, query: str) -> List[MCPServerTemplate]:
        """Search servers by name or description."""
        query_lower = query.lower()
        return [
            s for s in self.servers.values()
            if query_lower in s.name.lower() or query_lower in s.description.lower()
        ]
    
    def import_template(self, template_dict: Dict[str, Any]) -> bool:
        """Import server template from dictionary."""
        try:
            server = MCPServerTemplate(
                name=template_dict["name"],
                description=template_dict["description"],
                command=template_dict["command"],
                args=template_dict["args"],
                env=template_dict.get("env", {}),
                category=template_dict["category"],
                requires_api_key=template_dict.get("requires_api_key", False),
                api_key_env=template_dict.get("api_key_env", ""),
                auto_approve=template_dict.get("auto_approve")
            )
            return self.register(server)
        except Exception as e:
            print(f"❌ Failed to import template: {e}")
            return False
    
    def export_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Export server template to dictionary."""
        server = self.get(name)
        if server:
            return server.to_dict()
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        categories = {}
        for server in self.servers.values():
            categories[server.category] = categories.get(server.category, 0) + 1
        
        return {
            "total_servers": len(self.servers),
            "categories": categories,
            "requires_api_key": len([s for s in self.servers.values() if s.requires_api_key])
        }
    
    def _save(self):
        """Save registry to disk."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        data = {
            "templates": {
                name: server.to_dict()
                for name, server in self.servers.items()
            }
        }
        
        with open(self.registry_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def _load(self):
        """Load registry from disk."""
        if not os.path.exists(self.registry_file):
            return
        
        try:
            with open(self.registry_file, "r") as f:
                data = json.load(f)
            
            for name, template_dict in data.get("templates", {}).items():
                server = MCPServerTemplate(
                    name=template_dict["name"],
                    description=template_dict["description"],
                    command=template_dict["command"],
                    args=template_dict["args"],
                    env=template_dict.get("env", {}),
                    category=template_dict["category"],
                    requires_api_key=template_dict.get("requires_api_key", False),
                    api_key_env=template_dict.get("api_key_env", ""),
                    auto_approve=template_dict.get("auto_approve")
                )
                self.servers[name] = server
        except Exception as e:
            print(f"⚠️  Failed to load registry: {e}")


# Example templates for users to add
EXAMPLE_TEMPLATES = {
    "github": {
        "name": "github",
        "description": "GitHub API integration - repos, issues, PRs",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": ""},
        "category": "development",
        "requires_api_key": True,
        "api_key_env": "GITHUB_PERSONAL_ACCESS_TOKEN",
        "auto_approve": ["search_repositories", "get_file_contents"]
    },
    "filesystem": {
        "name": "filesystem",
        "description": "File system operations - read, write, search files",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"],
        "env": {},
        "category": "filesystem",
        "auto_approve": ["read_file", "list_directory"]
    },
    "postgres": {
        "name": "postgres",
        "description": "PostgreSQL database operations",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"],
        "env": {},
        "category": "database",
        "auto_approve": ["list_tables", "describe_table"]
    }
}
