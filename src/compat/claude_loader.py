"""
Claude Code compatibility loaders.

This module discovers commands, agents, skills, and MCP configs from standard
Claude Code directories. It does not execute any code; it only enumerates files.
"""

from __future__ import annotations

import os
from typing import List


def _expand(path: str) -> str:
    return os.path.expanduser(path)


def _discover_markdown_files(paths: List[str], glob_name: str) -> List[str]:
    files: List[str] = []
    for base in paths:
        if not os.path.isdir(base):
            continue
        for root, _, filenames in os.walk(base):
            for name in filenames:
                if name.endswith(glob_name):
                    files.append(os.path.join(root, name))
    return sorted(set(files))


def discover_claude_commands() -> List[str]:
    return _discover_markdown_files(
        [_expand("~/.claude/commands"), _expand("./.claude/commands")], ".md"
    )


def discover_claude_agents() -> List[str]:
    return _discover_markdown_files(
        [_expand("~/.claude/agents"), _expand("./.claude/agents")], ".md"
    )


def discover_claude_skills() -> List[str]:
    skills: List[str] = []
    for base in [_expand("~/.claude/skills"), _expand("./.claude/skills")]:
        if not os.path.isdir(base):
            continue
        for root, dirs, filenames in os.walk(base):
            if "SKILL.md" in filenames:
                skills.append(os.path.join(root, "SKILL.md"))
            for d in list(dirs):
                if d.startswith("."):
                    dirs.remove(d)
    return sorted(set(skills))


def discover_claude_mcps() -> List[str]:
    paths = [
        _expand("~/.claude/.mcp.json"),
        _expand("./.mcp.json"),
        _expand("./.claude/.mcp.json"),
    ]
    return [p for p in paths if os.path.exists(p)]
