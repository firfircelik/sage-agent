#!/usr/bin/env python3
"""
Sage Agent CLI for OpenCode integration.
"""

import sys
import argparse
import json
from typing import List
from src.opencode import AdvancedOpenCodeCLIAgent
from src.llm import LLMFactory
from src.utils import ModelRegistry
from src.utils import (
    install_opencode_plugin,
    uninstall_opencode_plugin,
    install_claude_mcp,
    uninstall_claude_mcp,
    doctor as doctor_check,
)


def _build_run_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sage Agent CLI (OpenCode)")
    parser.add_argument("--provider", default="openai", help="LLM provider")
    parser.add_argument("--model", help="Model name")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--rlm", action="store_true", default=True, help="Enable RLM optimization")
    parser.add_argument("--list-models", action="store_true", help="List all available models")
    return parser


def _build_full_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sage Agent CLI")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run OpenCode agent")
    run_parser.add_argument("--provider", default="openai", help="LLM provider")
    run_parser.add_argument("--model", help="Model name")
    run_parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    run_parser.add_argument("--rlm", action="store_true", default=True, help="Enable RLM optimization")
    run_parser.add_argument("--list-models", action="store_true", help="List all available models")

    install_parser = subparsers.add_parser("install", help="Install OpenCode/Claude integrations")
    install_parser.add_argument("--opencode", action="store_true", help="Install OpenCode plugin only")
    install_parser.add_argument("--claude", action="store_true", help="Install Claude MCP only")

    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall OpenCode/Claude integrations")
    uninstall_parser.add_argument("--opencode", action="store_true", help="Uninstall OpenCode plugin only")
    uninstall_parser.add_argument("--claude", action="store_true", help="Uninstall Claude MCP only")

    subparsers.add_parser("doctor", help="Check integration status")
    subparsers.add_parser("config", help="Print configuration paths")

    return parser


def _handle_run(args: argparse.Namespace) -> None:
    print("🔍 Discovering OpenCode models...")
    registry = ModelRegistry(auto_discover_opencode=True)

    if args.list_models:
        stats = registry.get_stats()
        print(f"\n📊 Available Models ({stats['total_models']} total):")
        print(f"   OpenCode discovered: {stats['opencode_discovered']}")
        print("\nModels:")
        for model in registry.list_models():
            source = model.metadata.get("source", "builtin")
            print(f"   • {model.name} ({model.provider.value}) [{source}]")
        return

    try:
        llm_kwargs = {}
        if args.model:
            llm_kwargs["model"] = args.model

        llm = LLMFactory.create(args.provider, **llm_kwargs)
        print(f"✅ LLM Provider: {args.provider}")
    except Exception as e:
        print(f"⚠️  LLM Provider error: {e}")
        llm = None

    agent = AdvancedOpenCodeCLIAgent(
        name="OpenCode Master",
        role="OpenCode CLI Expert",
        goal="Manage and optimize OpenCode operations",
        backstory="Expert in OpenCode CLI with advanced capabilities",
        llm_provider=llm,
        enable_rlm=args.rlm
    )

    print(f"🤖 Agent: {agent.name}")
    print(f"📊 OpenCode models: {len(agent.available_models)}")
    print(f"📊 Total models in registry: {registry.get_stats()['total_models']}")
    print(f"🔧 RLM enabled: {args.rlm}")

    if args.interactive:
        agent.interactive_mode()
    else:
        stats = agent.get_opencode_stats()
        print("\n📈 OpenCode Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")


def _parse_args(argv: List[str]) -> argparse.Namespace:
    if len(argv) > 1 and argv[1] in {"install", "uninstall", "doctor", "config", "run"}:
        parser = _build_full_parser()
        return parser.parse_args(argv[1:])

    parser = _build_run_parser()
    args = parser.parse_args(argv[1:])
    args.command = "run"
    return args


def main():
    args = _parse_args(sys.argv)

    if args.command == "install":
        if not args.opencode and not args.claude:
            args.opencode = True
            args.claude = True

        if args.opencode:
            ok, msg = install_opencode_plugin()
            print("✅" if ok else "⚠️", msg)
        if args.claude:
            ok, msg = install_claude_mcp()
            print("✅" if ok else "⚠️", msg)
        return

    if args.command == "uninstall":
        if not args.opencode and not args.claude:
            args.opencode = True
            args.claude = True

        if args.opencode:
            ok, msg = uninstall_opencode_plugin()
            print("✅" if ok else "⚠️", msg)
        if args.claude:
            ok, msg = uninstall_claude_mcp()
            print("✅" if ok else "⚠️", msg)
        return

    if args.command == "doctor":
        report = doctor_check()
        print(json.dumps(report, indent=2))
        return

    if args.command == "config":
        report = doctor_check()
        print(json.dumps({
            "opencode_config_path": report["opencode_config_path"],
            "claude_config_path": report["claude_config_path"],
            "python_executable": report["python_executable"]
        }, indent=2))
        return

    _handle_run(args)


if __name__ == "__main__":
    main()
