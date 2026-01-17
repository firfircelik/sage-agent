#!/bin/bash

# Multi-Agent RLM Installer
# Automatic setup for OpenCode CLI and Claude Code CLI

set -e

echo "🚀 Multi-Agent RLM Installer"
echo "============================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get installation directory
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}Installation directory: ${INSTALL_DIR}${NC}"
echo ""

# Check Python
echo "🔍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"
echo ""

# Automatically install for both CLIs
echo "📦 Installing for both OpenCode CLI and Claude Code CLI..."
CLI_CHOICE=3

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r "${INSTALL_DIR}/requirements.txt" --quiet

# Optional: semantic search (skip by default - user can install later)
echo ""
echo "⏭️  Skipping semantic search (install later with: pip install sentence-transformers)"

# Setup API keys
echo ""
echo "🔑 API Key Setup"
echo "==============="
echo ""

setup_api_keys() {
    local env_file="${INSTALL_DIR}/.env"
    
    echo "API keys can be configured later in .env file"
    echo "Creating empty .env template..."
    echo ""
    
    # Create .env file with empty values
    cat > "$env_file" << EOF
# LLM Provider API Keys
# Add your keys here after installation
OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""
DEEPSEEK_API_KEY=""
GLM_API_KEY=""
EOF
    
    echo -e "${GREEN}✅ .env file created (edit it to add your API keys)${NC}"
}

setup_api_keys

# Setup based on choice
case $CLI_CHOICE in
    1)
        echo ""
        echo "🔧 Setting up for OpenCode CLI..."
        
        # Create launcher script
        cat > "${INSTALL_DIR}/run.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source .env 2>/dev/null || true
python3 cli.py "$@"
EOF
        chmod +x "${INSTALL_DIR}/run.sh"
        
        echo -e "${GREEN}✅ OpenCode CLI setup complete!${NC}"
        echo ""
        echo "To use:"
        echo "  cd ${INSTALL_DIR}"
        echo "  ./run.sh --interactive"
        ;;
        
    2)
        echo ""
        echo "🔧 Setting up for Claude Code CLI..."
        
        # Detect Claude Code config location
        if [[ "$OSTYPE" == "darwin"* ]]; then
            CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            CLAUDE_CONFIG="$HOME/.config/Claude/claude_desktop_config.json"
        else
            CLAUDE_CONFIG="$HOME/.claude/claude_desktop_config.json"
        fi
        
        # Create config directory
        mkdir -p "$(dirname "$CLAUDE_CONFIG")"
        
        # Read existing config or create new
        if [ -f "$CLAUDE_CONFIG" ]; then
            echo "📝 Updating existing Claude Code config..."
            EXISTING_CONFIG=$(cat "$CLAUDE_CONFIG")
        else
            EXISTING_CONFIG='{"mcpServers":{}}'
        fi
        
        # Add our MCP server
        python3 << EOF
import json
import sys

config_file = "${CLAUDE_CONFIG}"
install_dir = "${INSTALL_DIR}"

# Read existing config
try:
    with open(config_file, 'r') as f:
        config = json.load(f)
except:
    config = {"mcpServers": {}}

# Ensure mcpServers exists
if "mcpServers" not in config:
    config["mcpServers"] = {}

# Add our server
config["mcpServers"]["multi-agent-rlm"] = {
    "command": "python3",
    "args": [f"{install_dir}/mcp_server.py"],
    "env": {
        "OPENAI_API_KEY": "",
        "ANTHROPIC_API_KEY": "",
        "DEEPSEEK_API_KEY": "",
        "GLM_API_KEY": ""
    }
}

# Save config
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print(f"✅ MCP server added to {config_file}")
EOF
        
        echo -e "${GREEN}✅ Claude Code CLI setup complete!${NC}"
        echo ""
        echo "To use:"
        echo "  1. Restart Claude Code"
        echo "  2. The 'multi-agent-rlm' tool will be available"
        echo "  3. Ask Claude to use it: 'Can you use multi-agent-rlm to process this?'"
        ;;
        
    3)
        echo ""
        echo "🔧 Setting up for both OpenCode and Claude Code..."
        
        # OpenCode setup
        cat > "${INSTALL_DIR}/run.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source .env 2>/dev/null || true
python3 cli.py "$@"
EOF
        chmod +x "${INSTALL_DIR}/run.sh"
        
        # Claude Code setup
        if [[ "$OSTYPE" == "darwin"* ]]; then
            CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            CLAUDE_CONFIG="$HOME/.config/Claude/claude_desktop_config.json"
        else
            CLAUDE_CONFIG="$HOME/.claude/claude_desktop_config.json"
        fi
        
        mkdir -p "$(dirname "$CLAUDE_CONFIG")"
        
        python3 << EOF
import json

config_file = "${CLAUDE_CONFIG}"
install_dir = "${INSTALL_DIR}"

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
except:
    config = {"mcpServers": {}}

if "mcpServers" not in config:
    config["mcpServers"] = {}

config["mcpServers"]["multi-agent-rlm"] = {
    "command": "python3",
    "args": [f"{install_dir}/mcp_server.py"],
    "env": {
        "OPENAI_API_KEY": "",
        "ANTHROPIC_API_KEY": "",
        "DEEPSEEK_API_KEY": "",
        "GLM_API_KEY": ""
    }
}

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)
EOF
        
        echo -e "${GREEN}✅ Both setups complete!${NC}"
        echo ""
        echo "OpenCode CLI:"
        echo "  cd ${INSTALL_DIR}"
        echo "  ./run.sh --interactive"
        echo ""
        echo "Claude Code CLI:"
        echo "  Restart Claude Code and use 'multi-agent-rlm' tool"
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Create uninstaller
cat > "${INSTALL_DIR}/uninstall.sh" << 'EOF'
#!/bin/bash
echo "🗑️  Uninstalling Multi-Agent RLM..."

# Remove from Claude Code config
if [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CLAUDE_CONFIG="$HOME/.config/Claude/claude_desktop_config.json"
else
    CLAUDE_CONFIG="$HOME/.claude/claude_desktop_config.json"
fi

if [ -f "$CLAUDE_CONFIG" ]; then
    python3 << PYEOF
import json
config_file = "${CLAUDE_CONFIG}"
try:
    with open(config_file, 'r') as f:
        config = json.load(f)
    if "mcpServers" in config and "multi-agent-rlm" in config["mcpServers"]:
        del config["mcpServers"]["multi-agent-rlm"]
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Removed from Claude Code config")
except:
    pass
PYEOF
fi

echo "✅ Uninstall complete"
echo "Note: Python packages and cache files remain"
echo "To remove completely: rm -rf $(dirname "$0")"
EOF

chmod +x "${INSTALL_DIR}/uninstall.sh"

# Summary
echo ""
echo "=============================="
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "=============================="
echo ""
echo "📚 Documentation:"
echo "  - README.md - Main guide"
echo "  - QUICKSTART.md - Quick start"
echo "  - CLAUDE_CODE_SETUP.md - Claude Code details"
echo ""
echo "🔧 Installed files:"
echo "  - .env - API keys"
echo "  - run.sh - OpenCode launcher (if selected)"
echo "  - uninstall.sh - Uninstaller"
echo ""
echo "💡 Next steps:"
if [[ $CLI_CHOICE == "1" ]] || [[ $CLI_CHOICE == "3" ]]; then
    echo "  ./run.sh --interactive"
fi
if [[ $CLI_CHOICE == "2" ]] || [[ $CLI_CHOICE == "3" ]]; then
    echo "  Restart Claude Code"
fi
echo ""
echo "🎉 Happy coding!"
