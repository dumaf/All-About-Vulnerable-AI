#!/bin/bash
# Startup wrapper for the Flask backend, auto-detecting the virtualenv directory.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check standard venv paths
if [ -d "$PROJECT_ROOT/AAVAI" ]; then
    VENV_PATH="$PROJECT_ROOT/AAVAI"
elif [ -d "$PROJECT_ROOT/venv" ]; then
    VENV_PATH="$PROJECT_ROOT/venv"
elif [ -d "$PROJECT_ROOT/.venv" ]; then
    VENV_PATH="$PROJECT_ROOT/.venv"
elif [ -d "$SCRIPT_DIR/AAVAI" ]; then
    VENV_PATH="$SCRIPT_DIR/AAVAI"
fi

if [ -n "$VENV_PATH" ]; then
    echo "Activating virtual environment at $VENV_PATH..."
    source "$VENV_PATH/bin/activate"
else
    echo "No virtual environment found, running with system python..."
fi

export PYTHONPATH="$PROJECT_ROOT"
python3 "$SCRIPT_DIR/app.py"
