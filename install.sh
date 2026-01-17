#!/bin/bash

# Sage Agent Installer
# Automatic setup for OpenCode CLI and Claude Code CLI

set -euo pipefail

echo "🚀 Sage Agent Installer"
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
SUPPORTED_PYTHON=(3.12 3.11 3.10 3.9)
PYTHON_BIN=""

version_in_range() {
    local version="$1"
    local major minor
    major=${version%%.*}
    minor=${version#*.}
    minor=${minor%%.*}
    [[ "$major" -eq 3 && "$minor" -ge 9 && "$minor" -le 12 ]]
}

find_supported_python() {
    for candidate in python3.12 python3.11 python3.10 python3.9 python3; do
        if ! command -v "$candidate" >/dev/null 2>&1; then
            continue
        fi
        local version
        version=$("$candidate" --version | awk '{print $2}')
        if version_in_range "$version"; then
            PYTHON_BIN=$(command -v "$candidate")
            echo "${GREEN}✅ Using Python ${version} (${candidate})${NC}"
            return 0
        fi
    done
    return 1
}

install_pyenv() {
    if command -v pyenv >/dev/null 2>&1; then
        echo "${YELLOW}pyenv already installed${NC}"
        return
    fi
    echo "${YELLOW}pyenv not found; installing now...${NC}"
    if [[ "${OSTYPE}" == "darwin"* ]] && command -v brew >/dev/null 2>&1; then
        brew install pyenv
    else
        curl https://pyenv.run | bash
    fi
    export PYENV_ROOT="${HOME}/.pyenv"
    export PATH="${PYENV_ROOT}/bin:$PATH"
    if command -v pyenv >/dev/null 2>&1; then
        eval "$(pyenv init --path)"
        eval "$(pyenv init -)"
    fi
}

install_supported_python() {
    install_pyenv
    local target_version="3.12.2"
    echo "${BLUE}Installing Python ${target_version} via pyenv...${NC}"
    PYENV_ROOT="${HOME}/.pyenv"
    export PYENV_ROOT
    export PATH="$PYENV_ROOT/bin:$PATH"
    if ! command -v pyenv >/dev/null 2>&1; then
        echo -e "${RED}❌ pyenv installation failed; please install Python 3.9-3.12 manually${NC}"
        exit 1
    fi
    pyenv install -s "$target_version"
    pyenv global "$target_version"
    PYTHON_BIN="${PYENV_ROOT}/versions/${target_version}/bin/python"
}

echo "🔍 Checking supported Python..."
if ! find_supported_python; then
    echo -e "${YELLOW}No supported Python executable found; attempting to install with pyenv${NC}"
    install_supported_python
fi
if [[ -z "${PYTHON_BIN}" ]]; then
    echo -e "${RED}❌ Failed to locate or install a supported Python (3.9-3.12)${NC}"
    exit 1
fi

PYTHON_VERSION=$("$PYTHON_BIN" --version | awk '{print $2}')
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} ready at ${PYTHON_BIN}${NC}"
echo ""

# Automatically install for both CLIs
echo "📦 Installing for both OpenCode CLI and Claude Code CLI..."
CLI_CHOICE=3

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ ! -d "${INSTALL_DIR}/venv" ]; then
    "$PYTHON_BIN" -m venv "${INSTALL_DIR}/venv"
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
"${INSTALL_DIR}/venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt" --quiet
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Optional: semantic search (skip by default - user can install later)
echo ""
echo "⏭️  Skipping semantic search (install later with: ./venv/bin/pip install sentence-transformers)"

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
source venv/bin/activate
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
        "$PYTHON_BIN" << EOF
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
config["mcpServers"]["sage-agent"] = {
    "command": f"{install_dir}/venv/bin/python3",
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
source venv/bin/activate
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
        
        "$PYTHON_BIN" << EOF
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

config["mcpServers"]["sage-agent"] = {
    "command": f"{install_dir}/venv/bin/python3",
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
        echo "  Restart Claude Code and use 'sage-agent' tool"
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Create uninstaller
cat > "${INSTALL_DIR}/uninstall.sh" << 'EOF'
#!/bin/bash
echo "🗑️  Uninstalling Sage Agent..."

# Remove from Claude Code config
if [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CLAUDE_CONFIG="$HOME/.config/Claude/claude_desktop_config.json"
else
    CLAUDE_CONFIG="$HOME/.claude/claude_desktop_config.json"
fi

if [ -f "$CLAUDE_CONFIG" ]; then
    /usr/bin/env python3 << PYEOF
import json
config_file = "${CLAUDE_CONFIG}"
try:
    with open(config_file, 'r') as f:
        config = json.load(f)
    if "mcpServers" in config and "sage-agent" in config["mcpServers"]:
        del config["mcpServers"]["sage-agent"]
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
