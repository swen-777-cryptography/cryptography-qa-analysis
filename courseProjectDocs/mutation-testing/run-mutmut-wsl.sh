#!/bin/bash
set -e

if [ ! -d ".venv-wsl" ]; then
    echo "Error: .venv-wsl not found. Please run setup-mutmut-wsl.sh first."
    exit 1
fi

echo "Activating WSL virtual environment..."
source .venv-wsl/bin/activate

echo "Clearing mutmut cache to ensure a fresh run..."
rm -rf .mutmut-cache mutants

echo "Running mutmut on src/cryptography/utils.py..."
mutmut run

echo ""
echo "=== Mutmut Results ==="
mutmut results

echo ""
echo "To view a specific mutant, run: source .venv-wsl/bin/activate && mutmut show <mutant-name>"

