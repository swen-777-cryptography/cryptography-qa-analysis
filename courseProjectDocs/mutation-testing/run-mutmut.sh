#!/bin/bash
set -e

# Detect virtual environment
if [ -d ".venv-wsl" ]; then
    VENV_PATH=".venv-wsl"
elif [ -d "courseProjectDocs/mutation-testing/.venv" ]; then
    VENV_PATH="courseProjectDocs/mutation-testing/.venv"
elif [ -d ".venv" ]; then
    VENV_PATH=".venv"
elif [ -n "$VIRTUAL_ENV" ]; then
    VENV_PATH="$VIRTUAL_ENV"
else
    echo "Error: Virtual environment not found (.venv-wsl, courseProjectDocs/mutation-testing/.venv, or .venv)."
    exit 1
fi

echo "Activating virtual environment ($VENV_PATH)..."
source "$VENV_PATH/bin/activate"

echo "Clearing mutmut cache to ensure a fresh run..."
rm -rf .mutmut-cache mutants

export OPENSSL_ENABLE_SHA1_SIGNATURES=1

echo "Running mutmut on src/cryptography/utils.py..."
mutmut run

echo ""
echo "=== Mutmut Results ==="
mutmut results

echo ""
echo "To view a specific mutant, run: source $VENV_PATH/bin/activate && mutmut show <mutant-name>"

