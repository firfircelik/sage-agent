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
