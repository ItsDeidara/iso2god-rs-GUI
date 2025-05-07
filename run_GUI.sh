#!/bin/sh
# Run the GUI application (GUI.py) using python3 if available, else fallback to python
SCRIPT_DIR="$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
    python3 "$SCRIPT_DIR/GUI.py"
else
    python "$SCRIPT_DIR/GUI.py"
fi 