#!/bin/bash

# Sage Agent Installation Verification Script

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔍 Sage Agent Installation Verification"
echo "======================================"
echo ""

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOTAL_CHECKS=0
PASSED_CHECKS=0

check_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASSED_CHECKS++))
    ((TOTAL_CHECKS++))
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((TOTAL_CHECKS++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
    ((TOTAL_CHECKS++))
}

echo "📁 File Structure Checks"
echo "----------------------------"

if [ -d "${INSTALL_DIR}/opencode-plugin/src" ]; then
    check_pass "opencode-plugin/src directory exists"
else
    check_fail "opencode-plugin/src directory missing"
fi

if [ -f "${INSTALL_DIR}/opencode-plugin/package.json" ]; then
    check_pass "opencode-plugin/package.json exists"
else
    check_fail "opencode-plugin/package.json missing"
fi

if [ -f "${INSTALL_DIR}/opencode-plugin/tsconfig.json" ]; then
    check_pass "opencode-plugin/tsconfig.json exists"
else
    check_fail "opencode-plugin/tsconfig.json missing"
fi

if [ -f "${INSTALL_DIR}/src/http_server.py" ]; then
    check_pass "src/http_server.py exists"
else
    check_fail "src/http_server.py missing"
fi

if [ -f "${INSTALL_DIR}/mcp_server.py" ]; then
    check_pass "mcp_server.py exists"
else
    check_fail "mcp_server.py missing"
fi

if [ -f "${INSTALL_DIR}/src/utils/installer.py" ]; then
    check_pass "src/utils/installer.py exists"
else
    check_fail "src/utils/installer.py missing"
fi

echo ""
echo "📦 Python Dependencies Check"
echo "------------------------------"

if grep -q "fastapi" "${INSTALL_DIR}/requirements.txt"; then
    check_pass "FastAPI in requirements.txt"
else
    check_fail "FastAPI not in requirements.txt"
fi

if grep -q "uvicorn" "${INSTALL_DIR}/requirements.txt"; then
    check_pass "Uvicorn in requirements.txt"
else
    check_fail "Uvicorn not in requirements.txt"
fi

echo ""
echo "📝 TypeScript Plugin Files Check"
echo "------------------------------------"

plugin_files=(
    "opencode-plugin/src/index.ts"
    "opencode-plugin/src/types.ts"
    "opencode-plugin/src/api/client.ts"
    "opencode-plugin/src/api/cache.ts"
    "opencode-plugin/src/tools/query.ts"
    "opencode-plugin/src/tools/memory.ts"
    "opencode-plugin/src/tools/knowledge.ts"
    "opencode-plugin/src/tools/learning.ts"
    "opencode-plugin/src/tools/stats.ts"
    "opencode-plugin/src/commands/loader.ts"
)

for file in "${plugin_files[@]}"; do
    if [ -f "${INSTALL_DIR}/${file}" ]; then
        check_pass "${file} exists"
    else
        check_fail "${file} missing"
    fi
done

echo ""
echo "📄 Slash Command Templates Check"
echo "--------------------------------"

command_files=(
    "opencode-plugin/src/command/sage.md"
    "opencode-plugin/src/command/memory.md"
    "opencode-plugin/src/command/stats.md"
    "opencode-plugin/src/command/learn.md"
    "opencode-plugin/src/command/optimize.md"
    "opencode-plugin/src/command/teach.md"
)

for file in "${command_files[@]}"; do
    if [ -f "${INSTALL_DIR}/${file}" ]; then
        check_pass "${file} exists"
    else
        check_fail "${file} missing"
    fi
done

echo ""
echo "🔧 Configuration Files Check"
echo "-------------------------------"

config_files=(
    "opencode-plugin/eslint.config.js"
    "opencode-plugin/.prettierrc"
    "opencode-plugin/.gitignore"
)

for file in "${config_files[@]}"; do
    if [ -f "${INSTALL_DIR}/${file}" ]; then
        check_pass "${file} exists"
    else
        check_fail "${file} missing"
    fi
done

echo ""
echo "📖 Documentation Check"
echo "-----------------------"

doc_files=(
    "opencode-plugin/README.md"
    "PLUGIN_QUICK_REFERENCE.md"
    "IMPLEMENTATION_SUMMARY.md"
)

for file in "${doc_files[@]}"; do
    if [ -f "${INSTALL_DIR}/${file}" ]; then
        check_pass "${file} exists"
    else
        check_fail "${file} missing"
    fi
done

echo ""
echo "🚀 Installer Check"
echo "-----------------"

if [ -f "${INSTALL_DIR}/install.sh" ]; then
    check_pass "install.sh exists"
else
    check_fail "install.sh missing"
fi

if [ -f "${INSTALL_DIR}/uninstall.sh" ]; then
    check_pass "uninstall.sh exists"
else
    check_fail "uninstall.sh missing"
fi

echo ""
echo "📊 Summary"
echo "==========="
echo ""
echo "Total checks: ${TOTAL_CHECKS}"
echo -e "${GREEN}Passed: ${PASSED_CHECKS}${NC}"
echo -e "${RED}Failed: $((TOTAL_CHECKS - PASSED_CHECKS))${NC}"
echo ""

if [ ${PASSED_CHECKS} -eq ${TOTAL_CHECKS} ]; then
    echo -e "${GREEN}🎉 All checks passed! Installation is complete.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some checks failed. Review above.${NC}"
    exit 1
fi
