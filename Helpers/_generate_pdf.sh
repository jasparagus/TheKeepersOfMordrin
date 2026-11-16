#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Prefer an existing virtualenv in Helpers/.venv or project root .venv
if [ -x "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
elif [ -x "$PROJECT_ROOT/.venv/bin/python" ]; then
    PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
else
    PYTHON_BIN="python3"
fi

# Auto-create Helpers/.venv and install requirements.txt if fpdf2 is missing
if ! "$PYTHON_BIN" -c "import fpdf" >/dev/null 2>&1; then
    echo "Setting up local Python environment in Helpers/.venv..."
    python3 -m venv "$SCRIPT_DIR/.venv"
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
    "$PYTHON_BIN" -m pip install --upgrade pip
    "$PYTHON_BIN" -m pip install -r "$SCRIPT_DIR/requirements.txt"
fi

"$PYTHON_BIN" "$SCRIPT_DIR/generate_pdf.py" "$@"

echo ""
read -rp "Press Enter to close..."
