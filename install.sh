#!/bin/bash

# Sage Agent Installer
# Automatic setup for OpenCode CLI and Claude Code CLI with HTTP Server

set -euo pipefail

echo "🚀 Sage Agent Installer (Production Edition)"
echo "========================================="
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

# Check Bun
echo "🔍 Checking Bun..."
if ! command -v bun >/dev/null 2>&1; then
    echo -e "${RED}❌ Bun not found. Please install: curl -fsSL https://bun.sh/install | bash${NC}"
    exit 1
fi
BUN_VERSION=$(bun --version)
echo -e "${GREEN}✅ Bun ${BUN_VERSION} found${NC}"
echo ""

# Automatically install for both CLIs
echo "📦 Installing for both OpenCode CLI and Claude Code CLI..."
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "${INSTALL_DIR}/venv" ]; then
    "$PYTHON_BIN" -m venv "${INSTALL_DIR}/venv"
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
"${INSTALL_DIR}/venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt" --quiet
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Optional: semantic search
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

# HTTP Server Configuration
SAGE_API_HOST=localhost
SAGE_API_PORT=8000
EOF
    
    echo -e "${GREEN}✅ .env file created (edit it to add your API keys)${NC}"
}

setup_api_keys

# Install TypeScript dependencies and build plugin
echo ""
echo "📦 Installing TypeScript dependencies..."
cd "${INSTALL_DIR}/opencode-plugin"
bun install 2>&1 | tail -5
echo -e "${GREEN}✅ TypeScript dependencies installed${NC}"

echo ""
echo "🔨 Building OpenCode plugin..."
bun run build 2>&1 | tail -10
echo -e "${GREEN}✅ OpenCode plugin built successfully${NC}"
cd "${INSTALL_DIR}"

# Create HTTP server launcher
echo ""
echo "🚀 Creating HTTP server launcher..."
cat > "${INSTALL_DIR}/start-server.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source .env 2>/dev/null || true
source venv/bin/activate

# Check if port is in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 8000 is already in use. Killing existing process..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo "🚀 Starting Sage Agent HTTP Server..."
echo "📊 API Documentation: http://localhost:8000/docs"
echo "📖 ReDoc: http://localhost:8000/redoc"
echo "💚 Health Check: http://localhost:8000/health"
echo ""
python src/http_server.py
EOF
chmod +x "${INSTALL_DIR}/start-server.sh"

# Start HTTP server in background
echo ""
echo "🚀 Starting HTTP server in background..."
nohup bash "${INSTALL_DIR}/start-server.sh" > "${INSTALL_DIR}/logs/server.log" 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Check if server started
if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}✅ HTTP server started (PID: $SERVER_PID)${NC}"
    echo -e "${GREEN}✅ Server running on http://localhost:8000${NC}"
else
    echo -e "${RED}❌ Failed to start HTTP server${NC}"
    echo "Check logs: tail -f ${INSTALL_DIR}/logs/server.log"
fi

# Create logs directory
mkdir -p "${INSTALL_DIR}/logs"

# OpenCode setup
echo ""
echo "🔧 Setting up OpenCode launcher..."
cat > "${INSTALL_DIR}/run.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source .env 2>/dev/null || true
source venv/bin/activate
python cli.py run "$@"
EOF
chmod +x "${INSTALL_DIR}/run.sh"

# Register OpenCode plugin + Claude MCP
echo ""
echo "📝 Registering plugin in OpenCode CLI..."
"${INSTALL_DIR}/venv/bin/python" "${INSTALL_DIR}/cli.py" install

# Verify installation
echo ""
echo "🔍 Verifying installation..."
sleep 2
DOCTOR_OUTPUT=$("${INSTALL_DIR}/venv/bin/python" "${INSTALL_DIR}/cli.py" doctor)
echo "$DOCTOR_OUTPUT" | grep -q '"opencode_plugin_registered": true' && \
    echo -e "${GREEN}✅ OpenCode CLI: Plugin registered successfully${NC}" || \
    echo -e "${YELLOW}⚠️  OpenCode CLI: Plugin registration may need manual verification${NC}"

echo "$DOCTOR_OUTPUT" | grep -q '"claude_mcp_registered": true' && \
    echo -e "${GREEN}✅ Claude Code CLI: MCP server registered successfully${NC}" || \
    echo -e "${YELLOW}⚠️  Claude Code CLI: MCP server registration may need manual verification${NC}"

# Check HTTP server health
sleep 2
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ HTTP Server: Running and healthy${NC}"
else
    echo -e "${YELLOW}⚠️  HTTP Server: Starting (check logs)${NC}"
fi

echo ""
echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo "📍 Plugin Location:"
echo "  ${INSTALL_DIR}/opencode-plugin/"
echo ""
echo "🎯 OpenCode CLI Integration:"
echo "  Config: ~/.config/opencode/opencode.json"
echo "  Usage: sage --interactive"
echo "         sage --list-models"
echo "         sage-stats"
echo ""
echo "🎯 Claude Code CLI Integration:"
if [[ "${OSTYPE}" == "darwin"* ]]; then
    echo "  Config: ~/Library/Application Support/Claude/claude_desktop_config.json"
else
    echo "  Config: ~/.config/Claude/claude_desktop_config.json"
fi
echo "  Usage: Use 'sage-agent' MCP tool in Claude Code"
echo "         Available tools: process_query, remember_interaction,"
echo "         provide_feedback, add_knowledge, get_stats, etc."
echo ""
echo "🚀 HTTP Server:"
echo "  URL: http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"
echo "  PID: $SERVER_PID"
echo "  Logs: ${INSTALL_DIR}/logs/server.log"
echo ""
echo "💡 Verify Installation:"
echo "  cd ${INSTALL_DIR}"
echo "  ./venv/bin/python cli.py doctor"
echo ""

cat > "${INSTALL_DIR}/uninstall.sh" << 'EOF'
#!/bin/bash
echo "🗑️  Uninstalling Sage Agent..."

# Stop HTTP server
if [ -f "$(dirname "$0")/logs/server.pid" ]; then
    PID=$(cat "$(dirname "$0")/logs/server.pid" 2>/dev/null || echo "")
    if [ ! -z "$PID" ]; then
        kill $PID 2>/dev/null || true
    fi
fi

# Kill server on port 8000
lsof -ti :8000 | xargs kill -9 2>/dev/null || true

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

# Save server PID
echo $SERVER_PID > "${INSTALL_DIR}/logs/server.pid"

# Summary
echo ""
echo "========================================="
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "========================================="
echo ""
echo "📚 Documentation:"
echo "  - README.md - Main guide"
echo "  - opencode-plugin/README.md - Plugin usage"
echo ""
echo "🔧 Installed files:"
echo "  - .env - API keys"
echo "  - start-server.sh - HTTP server launcher"
echo "  - run.sh - OpenCode launcher"
echo "  - uninstall.sh - Uninstaller"
echo ""
echo "💡 Next steps:"
echo "  1. Add API keys: nano .env"
echo "  2. Start OpenCode: ./run.sh --interactive"
echo "  3. Restart Claude Code to see MCP tool"
echo "  4. Check HTTP server health: curl http://localhost:8000/health"
echo "  5. View API docs: open http://localhost:8000/docs"
echo ""
echo "🚀 Server Management:"
echo "  Start: ./start-server.sh"
echo "  Stop: kill $(cat logs/server.pid)"
echo "  Logs: tail -f logs/server.log"
echo ""
echo "🎉 Happy coding!"
