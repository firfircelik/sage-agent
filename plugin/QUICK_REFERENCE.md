# Quick Reference: Using Sage Agent in OpenCode and Claude Code

## OpenCode CLI Commands

After installation, these commands are available:

### Interactive Mode
```bash
sage --interactive
```

### Direct Query
```bash
sage "Explain JWT authentication"
```

### List Models
```bash
sage --list-models
```

### With Specific Provider
```bash
sage --provider anthropic --model claude-3-sonnet "Your query here"
sage --provider deepseek --interactive
```

### View Statistics
```bash
sage-stats
```

### Query Memory
```bash
sage-memory "your search query"
```

## Claude Code CLI Usage

### Basic Usage
In Claude Code, mention the MCP tool in your conversation:

```
User: Use sage-agent to process this query: "Explain microservices architecture"
```

### Available MCP Methods

#### 1. process_query
Process a query with self-improvement and memory check
```json
{
  "method": "process_query",
  "params": {
    "query": "How to implement OAuth2?",
    "provider": "openai",
    "model": "gpt-4"
  }
}
```

#### 2. remember_interaction
Manually store an interaction
```json
{
  "method": "remember_interaction",
  "params": {
    "query": "Question asked",
    "response": "Answer given",
    "provider": "openai",
    "model": "gpt-4",
    "tokens_used": 1500,
    "success": true
  }
}
```

#### 3. provide_feedback
Submit feedback for learning
```json
{
  "method": "provide_feedback",
  "params": {
    "query": "Original question",
    "response": "Given answer",
    "feedback": "Great explanation!",
    "rating": 5
  }
}
```

#### 4. add_knowledge
Add to knowledge base
```json
{
  "method": "add_knowledge",
  "params": {
    "id": "security-jwt-001",
    "category": "security",
    "title": "JWT Best Practices",
    "content": "Always use HTTPS...",
    "tags": ["jwt", "security", "authentication"],
    "priority": 8
  }
}
```

#### 5. get_stats
View system statistics
```json
{
  "method": "get_stats"
}
```

#### 6. search_knowledge
Search knowledge base
```json
{
  "method": "search_knowledge",
  "params": {
    "query": "authentication",
    "category": "security",
    "limit": 5
  }
}
```

#### 7. recall_memory
Find similar past interactions
```json
{
  "method": "recall_memory",
  "params": {
    "query": "How to secure APIs?",
    "limit": 3
  }
}
```

## Verification

### Check if Plugin is Visible

```bash
# Quick check
./check-visibility.sh

# Detailed diagnostics
python cli.py doctor

# Expected output:
{
  "opencode_plugin_registered": true,    ← Visible in OpenCode
  "claude_mcp_registered": true,         ← Visible in Claude Code
  ...
}
```

## Troubleshooting

### Plugin Not Visible in OpenCode
```bash
# Re-register the plugin
python cli.py install --opencode

# Check config file
cat ~/.config/opencode/config.json

# Restart OpenCode CLI
```

### MCP Not Visible in Claude Code
```bash
# Re-register MCP server
python cli.py install --claude

# Check config file (macOS)
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Restart Claude Code application
```

### Both Not Working
```bash
# Re-run full installation
./install.sh

# Verify installation
./check-visibility.sh
```

## Configuration Files

### OpenCode Configuration
- **Path**: `~/.config/opencode/config.json`
- **Plugin Entry**: Points to plugin directory
- **Manifest**: `plugin/sage-agent.json`

### Claude Code Configuration
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **MCP Entry**: Points to `mcp_server.py` with python executable

## API Keys

Add your API keys to `.env` file:

```bash
nano .env
```

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=...
GLM_API_KEY=...
```

## Support

- GitHub Issues: https://github.com/firfircelik/sage-agent/issues
- Discussions: https://github.com/firfircelik/sage-agent/discussions
- Documentation: See README.md
