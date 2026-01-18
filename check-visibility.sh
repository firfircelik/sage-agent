#!/bin/bash

# Sage Agent - Check Plugin Visibility
# Verifies that sage-agent is visible in both OpenCode CLI and Claude Code CLI

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔍 Sage Agent - Plugin Visibility Check"
echo "========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if venv exists
if [ ! -d "${SCRIPT_DIR}/venv" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "   Run ./install.sh first"
    exit 1
fi

# Run doctor check
echo "📋 Running installation diagnostics..."
echo ""

DOCTOR_OUTPUT=$("${SCRIPT_DIR}/venv/bin/python" "${SCRIPT_DIR}/cli.py" doctor 2>/dev/null || echo '{}')

# Parse JSON (basic parsing)
OPENCODE_REGISTERED=$(echo "$DOCTOR_OUTPUT" | grep -o '"opencode_plugin_registered": [a-z]*' | awk '{print $2}' || echo "false")
CLAUDE_REGISTERED=$(echo "$DOCTOR_OUTPUT" | grep -o '"claude_mcp_registered": [a-z]*' | awk '{print $2}' || echo "false")
OPENCODE_PATH=$(echo "$DOCTOR_OUTPUT" | grep -o '"opencode_config_path": "[^"]*"' | cut -d'"' -f4 || echo "")
CLAUDE_PATH=$(echo "$DOCTOR_OUTPUT" | grep -o '"claude_config_path": "[^"]*"' | cut -d'"' -f4 || echo "")
PLUGIN_DIR=$(echo "$DOCTOR_OUTPUT" | grep -o '"opencode_plugin_dir": "[^"]*"' | cut -d'"' -f4 || echo "")

echo "🎯 OpenCode CLI Integration"
echo "----------------------------"
if [ "$OPENCODE_REGISTERED" = "true" ]; then
    echo -e "${GREEN}✅ Plugin is registered and visible${NC}"
    echo "   Config: ${OPENCODE_PATH}"
    echo "   Plugin: ${PLUGIN_DIR}"
    echo ""
    echo "   Usage:"
    echo "   • sage --interactive"
    echo "   • sage --list-models"
    echo "   • sage-stats"
else
    echo -e "${RED}❌ Plugin is NOT registered${NC}"
    echo "   Config: ${OPENCODE_PATH}"
    echo ""
    echo "   To fix: python cli.py install --opencode"
fi

echo ""
echo "🎯 Claude Code CLI Integration"
echo "-------------------------------"
if [ "$CLAUDE_REGISTERED" = "true" ]; then
    echo -e "${GREEN}✅ MCP server is registered and visible${NC}"
    echo "   Config: ${CLAUDE_PATH}"
    echo ""
    echo "   Usage in Claude Code:"
    echo "   • Use 'sage-agent' MCP tool"
    echo "   • Available methods: process_query, remember_interaction,"
    echo "     provide_feedback, add_knowledge, get_stats, etc."
    echo ""
    echo "   Note: Restart Claude Code to see the MCP tool"
else
    echo -e "${RED}❌ MCP server is NOT registered${NC}"
    echo "   Config: ${CLAUDE_PATH}"
    echo ""
    echo "   To fix: python cli.py install --claude"
fi

echo ""
echo "📊 Full Diagnostic Report"
echo "-------------------------"
echo "$DOCTOR_OUTPUT" | python3 -m json.tool 2>/dev/null || echo "$DOCTOR_OUTPUT"

echo ""
echo "💡 Troubleshooting"
echo "-----------------"
echo "If plugin is not visible:"
echo "  1. Run: ./install.sh           (re-install)"
echo "  2. Run: python cli.py install  (re-register)"
echo "  3. Check config files manually"
echo "  4. For OpenCode: Restart OpenCode CLI"
echo "  5. For Claude: Restart Claude Code app"
echo ""
