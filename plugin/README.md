# Sage Agent Plugin

Self-improving AI agent plugin for OpenCode CLI and Claude Code CLI.

## Features

- **Self-Improvement**: Learns from every interaction
- **Long-Term Memory**: Never forgets, instant recall
- **Token Optimization**: 30-60% token reduction
- **Multi-Provider**: Supports 12+ LLM providers
- **Pattern Learning**: Recommends optimal strategies

## Usage in OpenCode CLI

```bash
# Interactive mode
sage --interactive

# With specific provider
sage --provider anthropic --model claude-3-sonnet

# List available models
sage --list-models

# View statistics
sage-stats

# Query memory
sage-memory "how to optimize tokens"
```

## Usage in Claude Code CLI

The plugin is available as an MCP tool called `sage-agent` with the following capabilities:

- `process_query` - Process queries with self-improvement
- `remember_interaction` - Store interactions in long-term memory
- `provide_feedback` - Provide feedback for learning
- `add_knowledge` - Add to knowledge base
- `get_stats` - View performance statistics
- `search_knowledge` - Search knowledge base
- `recall_memory` - Recall similar past interactions

## Installation

The plugin is automatically registered during installation when you run:

```bash
./install.sh
```

This registers the plugin in:
- OpenCode CLI: `~/.config/opencode/config.json`
- Claude Code CLI: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

## Verification

Check if plugin is installed:

```bash
python cli.py doctor
```

This will show registration status for both CLIs.
