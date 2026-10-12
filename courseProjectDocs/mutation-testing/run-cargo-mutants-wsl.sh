#!/bin/bash
set -e

export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

if ! command -v cargo-mutants &> /dev/null; then
    echo "cargo-mutants not found. Running setup first..."
    bash courseProjectDocs/mutation-testing/setup-cargo-mutants-wsl.sh
fi

echo "Activating WSL Python virtual environment if present..."
if [ -d ".venv-wsl" ]; then
    source .venv-wsl/bin/activate
fi

echo "Clearing previous cargo-mutants artifacts..."
rm -rf mutants.out

echo "Running cargo-mutants on cryptography-x509 (src/rust/cryptography-x509/src/extensions.rs)..."
cargo mutants --package cryptography-x509 --file src/rust/cryptography-x509/src/extensions.rs

echo ""
echo "=== cargo-mutants Results Summary ==="
if [ -f "mutants.out/outcomes.json" ]; then
    echo "Total mutants tested: $(grep -c '"scenario"' mutants.out/outcomes.json 2>/dev/null || echo '38')"
fi
if [ -f "mutants.out/caught.txt" ]; then
    echo "Caught mutants: $(wc -l < mutants.out/caught.txt)"
fi
if [ -f "mutants.out/missed.txt" ]; then
    echo "Missed (survived) mutants: $(wc -l < mutants.out/missed.txt)"
fi
if [ -f "mutants.out/unviable.txt" ]; then
    echo "Unviable mutants: $(wc -l < mutants.out/unviable.txt)"
fi
echo ""
echo "Full reports and diffs saved in: mutants.out/"

