"""Compatibility helpers for Claude Code and OpenCode."""

from .claude_loader import (
    discover_claude_commands,
    discover_claude_agents,
    discover_claude_skills,
    discover_claude_mcps,
)

__all__ = [
    "discover_claude_commands",
    "discover_claude_agents",
    "discover_claude_skills",
    "discover_claude_mcps",
]
