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

echo ""
echo "🔧 Setting up for both OpenCode and Claude Code..."

# OpenCode setup
cat > "${INSTALL_DIR}/run.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source .env 2>/dev/null || true
source venv/bin/activate
python cli.py run "$@"
EOF
chmod +x "${INSTALL_DIR}/run.sh"

# Register OpenCode plugin + Claude MCP
"${INSTALL_DIR}/venv/bin/python" "${INSTALL_DIR}/cli.py" install

echo -e "${GREEN}✅ Both setups complete!${NC}"
echo ""
echo "OpenCode CLI:"
echo "  cd ${INSTALL_DIR}"
echo "  ./run.sh --interactive"
echo ""
echo "Claude Code CLI:"
echo "  Restart Claude Code and use 'sage-agent' tool"

cat > "${INSTALL_DIR}/uninstall.sh" << 'EOF'
#!/bin/bash
echo "🗑️  Uninstalling Sage Agent..."

if [ -x "$(dirname "$0")/venv/bin/python" ]; then
    "$(dirname "$0")/venv/bin/python" "$(dirname "$0")/cli.py" uninstall
else
    echo "⚠️  Python virtualenv not found. Remove integrations manually."
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
echo "  ./run.sh --interactive"
echo "  Restart Claude Code"
echo ""
echo "🎉 Happy coding!"
