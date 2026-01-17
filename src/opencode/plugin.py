"""
OpenCode plugin shim for Sage Agent.

This module provides install/uninstall helpers so OpenCode can register the plugin
name in its configuration. It does not require OpenCode SDK.
"""

from __future__ import annotations

from typing import Tuple
from ..utils.installer import install_opencode_plugin, uninstall_opencode_plugin


def register() -> Tuple[bool, str]:
    return install_opencode_plugin()


def unregister() -> Tuple[bool, str]:
    return uninstall_opencode_plugin()
