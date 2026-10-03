#!/usr/bin/env bash
# Creates a private virtual environment on first run, then launches Sri's Writer.
#   ./run.sh              run the application
#   ./run.sh --test       run the test suite
#   ./run.sh file.sri     open a document
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"

VENV=".venv"
MARKER="$VENV/.requirements-installed"

if [ ! -d "$VENV" ]; then
    echo "Creating virtual environment in $VENV ..."
    if ! python3 -m venv "$VENV"; then
        echo "Could not create a virtual environment."
        echo "On Debian/Ubuntu/Linux Mint run:  sudo apt install python3-venv"
        exit 1
    fi
fi

if [ ! -f "$MARKER" ] || [ requirements.txt -nt "$MARKER" ]; then
    echo "Installing dependencies ..."
    "$VENV/bin/python" -m pip install --upgrade pip >/dev/null
    "$VENV/bin/python" -m pip install -r requirements.txt
    touch "$MARKER"
fi

if [ "${1:-}" = "--test" ]; then
    "$VENV/bin/python" -m pip install pytest >/dev/null
    export QT_QPA_PLATFORM=offscreen
    exec "$VENV/bin/python" -m pytest -v tests
fi

exec "$VENV/bin/python" main.py "$@"
