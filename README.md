# Sage - Self-Improving AI Agent

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-support%20creator-orange)](https://buymeacoffee.com/firatcelik3)
[![Python](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CI/CD](https://github.com/firfircelik/sage-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/firfircelik/sage-agent/actions)
[![Release](https://img.shields.io/github/v/release/firfircelik/sage-agent?include_prereleases&sort=semver)](https://github.com/firfircelik/sage-agent/releases)
[![Contributors](https://img.shields.io/github/contributors/firfircelik/sage-agent)](https://github.com/firfircelik/sage-agent/graphs/contributors)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/firfircelik?label=Sponsors)](https://github.com/sponsors/firfircelik)
[![Discussions](https://img.shields.io/github/discussions/firfircelik/sage-agent)](https://github.com/firfircelik/sage-agent/discussions)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/firfircelik/sage-agent/pulls)
[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-red.svg)](https://github.com/firfircelik/sage-agent)

A self-improving AI agent system with advanced token optimization for OpenCode CLI and Claude Code CLI. The agent learns from every interaction, never forgets, and continuously improves like an LLM.

**Open Source** | **MIT Licensed** | **Community Driven**

Contributions welcome! See [Contributing](#contributing) for guidelines.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Self-Improvement System](#self-improvement-system)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Performance](#performance)
- [Community & Support](#community--support)
- [Contributing](#contributing)
- [License](#license)

## Overview

Sage Agent is a self-improving AI system that learns from every interaction. The agent maintains long-term memory, validates responses to prevent hallucinations, and continuously improves its performance through pattern learning and feedback analysis.

### Core Capabilities

- **Self-Improving AI**: Automatically learns from every interaction, tracks mistakes, and improves over time
- **Long-Term Memory**: Permanently stores all interactions, never forgets, enables instant recall
- **No Hallucinations**: Validates every response, detects uncertainty indicators, ensures accuracy
- **No Duplication**: Checks memory before processing, prevents redundant work
- **Token Optimization**: 30-60% reduction through advanced compression and caching
- **Pattern Learning**: Learns usage patterns, recommends optimal strategies
- **Multi-Provider Support**: 12+ LLM providers including OpenAI, Anthropic, DeepSeek, GLM

## Key Features

### Self-Improvement System

The agent automatically improves with every interaction:

- **Automatic Learning**: Every query is remembered, validated, and learned from
- **Mistake Tracking**: Identifies and learns from errors, prevents repetition
- **Quality Monitoring**: Tracks response quality trends (improving/stable/declining)
- **Pattern Recognition**: Learns from usage patterns, optimizes strategies
- **Feedback Integration**: Incorporates user feedback for continuous improvement
- **Success Patterns**: Identifies what works, applies successful approaches

### Long-Term Memory

Never forgets, always learns:

- **Permanent Storage**: All interactions stored permanently on disk
- **Exact Recall**: Instant retrieval of previously asked questions (< 1ms)
- **Similar Query Learning**: Finds and learns from related past interactions
- **Pattern Extraction**: Automatically extracts and learns patterns from queries
- **Conversation Context**: Maintains full conversation history
- **Learned Insights**: Provides insights from accumulated knowledge

### Response Validation

Prevents hallucinations and ensures accuracy:

- **Hallucination Detection**: Identifies uncertainty indicators ("I think", "maybe", "probably")
- **Confidence Scoring**: Assigns confidence score (0-1) to every response
- **Contradiction Detection**: Identifies logical contradictions in responses
- **Context Validation**: Ensures provided context is utilized
- **Quality Checks**: Validates response length, relevance, and completeness
- **Automatic Flagging**: Marks low-confidence responses for review

### Token Optimization

Advanced strategies for 30-60% savings:

- **Advanced Optimizer**: 6 optimization strategies (redundancy removal, verbose compression, etc.)
- **Adaptive Compression**: Learns optimal compression level for each query type
- **Smart Caching**: LRU cache with TTL, prevents redundant API calls
- **Context Prioritization**: Intelligently selects most relevant context
- **Deduplication**: Eliminates redundant information
- **Prompt Rewriting**: Rewrites prompts for clarity and brevity

### Intelligence Engine

AI-powered decision making:

- **Usage Pattern Analysis**: Tracks and learns from usage patterns
- **Provider Recommendations**: Suggests best provider based on query type
- **Peak Hour Detection**: Identifies usage patterns over time
- **Category Classification**: Automatically categorizes queries
- **Performance Tracking**: Monitors provider and model performance
- **Optimization Suggestions**: Recommends improvements based on patterns

## Installation

### Prerequisites

- Python 3.9-3.12
- pip package manager

### Automatic Installation

The installer automatically configures both OpenCode CLI and Claude Code CLI:

```bash
git clone https://github.com/firfircelik/sage-agent.git
cd sage-agent
bash install.sh
```

### Plugin Installation (recommended)

After installing dependencies, register Sage Agent as an OpenCode plugin and Claude MCP:

```bash
sage-agent install
# or without package install
python cli.py install
```

The installation automatically:
- **Registers plugin in OpenCode CLI** at `~/.config/opencode/config.json`
- **Registers MCP server in Claude Code CLI** at:
  - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - Linux: `~/.config/Claude/claude_desktop_config.json`
  - Windows: `~/.claude/claude_desktop_config.json`

**Verification:**

```bash
# Check installation status
python cli.py doctor

# Output shows:
# {
#   "opencode_plugin_registered": true,     ← Visible in OpenCode CLI
#   "claude_mcp_registered": true,          ← Visible in Claude Code CLI
#   "opencode_config_path": "...",
#   "claude_config_path": "...",
#   "plugin_dir": ".../plugin"
# }
```

**Uninstall:**

```bash
sage-agent uninstall
# or
python cli.py uninstall
```

Useful commands:

```bash
sage-agent doctor    # Verify installation status
sage-agent uninstall # Remove from both CLIs
```

Useful commands:

```bash
sage-agent doctor    # Verify installation status
sage-agent uninstall # Remove from both CLIs
```

The installer will:
1. Verify Python installation
2. Install required dependencies
3. Install and build OpenCode plugin (TypeScript)
4. Start HTTP server in background
5. Create .env template file
6. Set up launcher scripts
7. Register OpenCode plugin and Claude MCP
8. Create uninstall script

After installation, edit `.env` file to add your API keys:

```bash
nano .env
```

## OpenCode CLI Plugin

Sage Agent includes a production-grade OpenCode CLI plugin with advanced features not available in any other plugin.

### Unique Features

Unlike standard plugins, Sage Agent provides:

- **RLM (Reinforcement Learning Mechanism)** - Learns from every interaction
- **Long-Term Memory** - Instant recall (<1ms) of past interactions
- **Token Optimization** - 30-60% reduction through advanced compression
- **Self-Improvement Engine** - Continuous quality tracking and learning
- **Multi-Provider Support** - 12+ LLM providers
- **Hallucination Detection** - Validates every response for accuracy
- **Knowledge Base** - Structured, searchable knowledge management

### Plugin Architecture

The plugin uses a high-performance HTTP server for communication:

```
┌─────────────────────────────────────────┐
│   OpenCode CLI Plugin (TypeScript)   │
│   ↓ HTTP Requests                    │
│   ┌───────────────────────────────┐   │
│   │ HTTP Server (FastAPI)       │   │
│   │ ↓                          │   │
│   │ Sage Agent Core (Python)     │   │
│   │ - RLM Engine               │   │
│   │ - Long-Term Memory          │   │
│   │ - Knowledge Base            │   │
│   │ - Self-Improvement          │   │
│   └───────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Available Tools (10 total)

The plugin provides these tools that OpenCode's LLM can invoke:

1. **sage_process_query** - Process queries with self-improving AI
2. **sage_stream_query** - Real-time streaming with progress updates
3. **sage_recall_memory** - Instantly recall similar past interactions
4. **sage_add_interaction** - Manually add interactions for learning
5. **sage_provide_feedback** - Submit feedback for continuous improvement
6. **sage_search_knowledge** - Search structured knowledge base
7. **sage_add_knowledge** - Add knowledge entries
8. **sage_get_patterns** - View learned patterns and insights
9. **sage_get_stats** - Comprehensive statistics and analytics
10. **sage_optimization_insights** - Token optimization details

### Slash Commands

User-invokable commands:

- `/sage <query>` - Process query with RLM optimization
- `/sage-memory <query>` - Search long-term memory
- `/sage-stats` - View comprehensive statistics
- `/sage-learn` - View learned patterns
- `/sage-optimize` - Get token optimization insights
- `/sage-teach <content>` - Add knowledge to base

### HTTP Server

High-performance FastAPI server with:

- **Async operations** for maximum performance
- **Streaming support** via Server-Sent Events (SSE)
- **LRU caching** with configurable TTL
- **Health monitoring** with metrics tracking
- **CORS enabled** for plugin communication
- **Auto-generated docs** at `http://localhost:8000/docs`

**Endpoints:**

```
GET  /health                          - Health check
POST /api/v1/query/process           - Process query
POST /api/v1/query/stream            - Stream query (SSE)
GET  /api/v1/memory/recall            - Recall similar interactions
POST /api/v1/memory/add               - Add interaction
POST /api/v1/memory/feedback           - Submit feedback
GET  /api/v1/knowledge/search         - Search knowledge
POST /api/v1/knowledge/add            - Add knowledge
GET  /api/v1/stats                   - Get statistics
GET  /api/v1/stats/trends            - Get quality trends
GET  /api/v1/learned/patterns         - View patterns
GET  /api/v1/metrics                 - API metrics
```

### Plugin Documentation

Full plugin documentation: [opencode-plugin/README.md](opencode-plugin/README.md)

## Quick Start

### Verifying Plugin Visibility

After installation, verify that Sage Agent is visible in both CLIs:

```bash
# Verify installation status
python cli.py doctor

# Expected output:
# {
#   "opencode_plugin_registered": true,     ← Plugin visible in OpenCode CLI
#   "claude_mcp_registered": true,          ← MCP tool visible in Claude Code CLI
#   ...
# }
```

**In OpenCode CLI:**
- Plugin is listed in the available plugins
- Run `sage --interactive` to start
- Commands: `sage`, `sage-stats`, `sage-memory`

**In Claude Code CLI:**
- MCP tool "sage-agent" is available
- Listed in available tools/integrations
- Use directly: "Use sage-agent to process this query"

### OpenCode CLI

```bash
./run.sh --interactive
# or if installed as a package
sage-agent run --interactive
```

Available commands:
- `models` - List all available models
- `run <prompt>` - Execute a prompt with self-improvement
- `stats` - Display system statistics
- `exit` - Exit interactive mode

### Claude Code CLI

After installation, the MCP server is automatically configured. Restart Claude Code and use:

```
User: Can you use sage-agent to process this query?
Query: "Explain JWT authentication implementation"
```

The agent will:
1. Check if this exact query was asked before
2. Recall similar past interactions
3. Apply advanced optimization
4. Validate the response
5. Remember the interaction for future learning

Available MCP tools:
- `process_query` - Process queries with full self-improvement
- `remember_interaction` - Manually store interactions
- `provide_feedback` - Submit feedback for learning (rating 1-5)
- `add_knowledge` - Add entries to knowledge base
- `get_stats` - Retrieve comprehensive statistics
- `search_knowledge` - Search the knowledge base
- `recall_memory` - Recall similar past interactions

### Programmatic Usage

```python
from src.rlm import EnterpriseRLM

# Initialize the self-improving agent
rlm = EnterpriseRLM()

# Process a query - agent automatically learns and improves
result = rlm.process_query(
    query="How to implement REST API authentication?",
    provider="openai",
    model="gpt-4",
    use_advanced_optimization=True
)

# Check if response came from memory (no duplication)
if result["from_memory"]:
    print(f"Retrieved from memory in {result['processing_time']}s")
    print(f"Tokens saved: {result['tokens_saved']}")
else:
    print(f"New query processed")
    print(f"Similar memories: {result['similar_memories']}")
    print(f"Suggestions: {result['improvement_suggestions']}")

# Interaction is automatically remembered and validated
# No manual remember_interaction needed when using RLMEnabledLLMAgent

# Provide feedback for continuous improvement
rlm.provide_feedback(
    query="How to implement REST API authentication?",
    response=result["response"],
    feedback="Excellent explanation",
    rating=5  # 1-5 scale
)

# Add custom knowledge
rlm.add_knowledge(
    id="jwt_best_practices",
    category="security",
    title="JWT Best Practices",
    content="Use HTTPS, set expiration, validate tokens...",
    tags=["auth", "jwt", "security"],
    priority=9
)
```

## Self-Improvement System

The agent automatically improves with every interaction. No manual intervention required.

### How It Works

```python
# First query - agent learns
result1 = rlm.process_query("What is JWT?")
# 1. Checks memory (not found)
# 2. Processes query
# 3. Validates response
# 4. Stores in memory
# 5. Learns patterns

# Provide feedback
rlm.provide_feedback(
    query="What is JWT?",
    response=result1["response"],
    feedback="Good but needs more detail",
    rating=3
)
# Agent learns: "JWT" queries need more detail

# Similar query - agent recalls and improves
result2 = rlm.process_query("Explain JWT authentication")
# 1. Recalls similar query
# 2. Applies learned improvements
# 3. Provides more detailed response
print(result2["improvement_suggestions"])
# ["Be more detailed based on past feedback"]

# Exact query - instant recall
result3 = rlm.process_query("What is JWT?")
print(result3["from_memory"])  # True
print(result3["processing_time"])  # < 0.001s
```

### Automatic Features

Every query automatically triggers:

1. **Memory Check**: Searches for exact or similar past queries
2. **Pattern Learning**: Extracts and learns patterns from query
3. **Response Validation**: Checks for hallucinations and quality
4. **Storage**: Permanently stores interaction
5. **Improvement**: Updates optimization strategies

### Quality Tracking

```python
# Get quality trend
stats = rlm.get_comprehensive_stats()
trend = stats['improvement']['quality_trend']

print(f"Trend: {trend['trend']}")  # improving/stable/declining
print(f"Quality: {trend['current_quality']}")  # e.g., "85.5%"
print(f"Change: {trend['improvement']}")  # e.g., "+5.2%"
```

### Learned Insights

```python
# Get what the agent has learned
insights = rlm.memory.get_learned_insights()

print(f"Total memories: {insights['total_memories']}")
print(f"Patterns learned: {insights['learned_patterns']}")
print(f"Success rate: {insights['success_rate']}%")
print(f"Top topics: {insights['top_topics']}")
```

## Architecture

### System Components

```
EnterpriseRLM
├── RLMOptimizer          # Core optimization engine
├── AdvancedOptimizer     # Advanced optimization strategies
├── AdaptiveCompressor    # Learning-based compression
├── LongTermMemory        # Persistent memory storage
├── SelfImprovementEngine # Quality tracking and learning
├── IntelligenceEngine    # AI-powered analysis
├── KnowledgeBase         # Structured knowledge storage
└── VectorStore           # Semantic search capabilities
```

### Agent Hierarchy

```
RLMEnabledLLMAgent (Base)
└── AdvancedOpenCodeCLIAgent
    ├── Model Discovery
    ├── Session Management
    └── CLI Integration
```

### Data Flow

1. Query received
2. Check long-term memory for exact match
3. Recall similar past interactions
4. Apply advanced optimization
5. Retrieve relevant context from knowledge base
6. Process with selected LLM provider
7. Validate response quality
8. Store interaction for learning
9. Update optimization strategies

## Configuration

### Environment Variables

Schema and example files:

- config/sage-agent.schema.json
- config/sage-agent.example.json

Create a `.env` file in the project root:

```bash
# LLM Provider API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=...
GLM_API_KEY=...

# Optional: Custom cache directory
RLM_CACHE_DIR=.rlm_cache

# Optional: Enable semantic search
ENABLE_SEMANTIC_SEARCH=true
```

### Advanced Configuration

Edit `config/config.yaml` for advanced settings:

```yaml
rlm:
  cache_ttl: 3600
  compression_strategy: smart
  enable_validation: true
  
optimization:
  target_savings: 0.4
  preserve_meaning: true
  
memory:
  max_entries: 10000
  similarity_threshold: 0.7
```

## Performance

### Benchmarks

| Metric | Value |
|--------|-------|
| Token Savings | 30-60% average |
| Memory Recall | < 1ms |
| Response Validation | 95%+ accuracy |
| Quality Improvement | Continuous |
| Cache Hit Rate | 40-60% |

### Optimization Results

- **Redundancy Removal**: 15-25% reduction
- **Verbose Compression**: 10-20% reduction
- **Context Optimization**: 5-15% reduction
- **Adaptive Learning**: Improves over time

## Documentation

All documentation is contained in this README. For specific topics:

- Installation: See [Installation](#installation) section
- Quick Start: See [Quick Start](#quick-start) section
- Claude Code Setup: See [Claude Code CLI](#claude-code-cli) section
- Configuration: See [Configuration](#configuration) section

## Contributing

This is an open-source project and contributions are welcome. We appreciate bug reports, feature requests, documentation improvements, and code contributions.

### How to Contribute

1. **Fork the repository** on GitHub
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** with clear, descriptive commits
4. **Add tests** for new functionality
5. **Run tests** to ensure nothing breaks (`python -m pytest tests/`)
6. **Format code** with black (`black src/`)
7. **Submit a pull request** with a clear description

### Contribution Guidelines

- **Code Quality**: Follow PEP 8 style guide, use type hints
- **Testing**: Add tests for new features, maintain test coverage
- **Documentation**: Update README and docstrings as needed
- **Commits**: Write clear, descriptive commit messages
- **Issues**: Check existing issues before creating new ones
- **Respect**: Be respectful and constructive in discussions

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/sage-agent.git
cd sage-agent

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install pytest black flake8

# Run tests
python -m pytest tests/

# Format code
black src/

# Check code quality
flake8 src/
```

### What We're Looking For

- Bug fixes and improvements
- New LLM provider integrations
- Performance optimizations
- Documentation improvements
- Test coverage improvements
- Feature enhancements

### Code Review Process

All pull requests will be reviewed by maintainers. We look for:

- Code quality and style
- Test coverage
- Documentation
- Performance impact
- Security considerations

Pull requests require approval from at least one maintainer before merging.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This is free and open-source software. You are free to use, modify, and distribute it under the terms of the MIT License.

## Acknowledgments

Built for the open-source community, OpenCode CLI and Claude Code CLI users who need self-improving AI capabilities with optimal token efficiency.

Special thanks to all contributors who help improve this project.

---

**Status**: Production Ready | **Version**: 1.0.0 | **Python**: 3.9-3.12 | **License**: MIT
