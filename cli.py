#!/usr/bin/env python3
"""
Multi-Agent System CLI for OpenCode integration.
"""

import sys
import argparse
from src.opencode import AdvancedOpenCodeCLIAgent
from src.llm import LLMFactory
from src.utils import ModelRegistry


def main():
    parser = argparse.ArgumentParser(description='Multi-Agent System for OpenCode')
    parser.add_argument('--provider', default='openai', help='LLM provider')
    parser.add_argument('--model', help='Model name')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--rlm', action='store_true', default=True, help='Enable RLM optimization')
    parser.add_argument('--list-models', action='store_true', help='List all available models')
    
    args = parser.parse_args()
    
    # Auto-discover OpenCode models
    print("🔍 Discovering OpenCode models...")
    registry = ModelRegistry(auto_discover_opencode=True)
    
    if args.list_models:
        print(f"\n📊 Available Models ({registry.get_stats()['total_models']} total):")
        print(f"   OpenCode discovered: {registry.get_stats()['opencode_discovered']}")
        print("\nModels:")
        for model in registry.list_models():
            source = model.metadata.get('source', 'builtin')
            print(f"   • {model.name} ({model.provider.value}) [{source}]")
        return
    
    # Create LLM provider
    try:
        llm_kwargs = {}
        if args.model:
            llm_kwargs['model'] = args.model
        
        llm = LLMFactory.create(args.provider, **llm_kwargs)
        print(f"✅ LLM Provider: {args.provider}")
    except Exception as e:
        print(f"⚠️  LLM Provider error: {e}")
        llm = None
    
    # Create agent
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
        # Show stats
        stats = agent.get_opencode_stats()
        print(f"\n📈 OpenCode Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")


if __name__ == "__main__":
    main()
