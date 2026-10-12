#!/bin/bash
set -e

echo "=== Setting up cargo-mutants for Rust Mutation Testing ==="

# Ensure ~/.cargo/bin and ~/.local/bin exist and are on PATH
mkdir -p "$HOME/.cargo/bin" "$HOME/.local/bin"
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

if ! command -v cargo-mutants &> /dev/null; then
    echo "Downloading prebuilt cargo-mutants binary..."
    CARGO_MUTANTS_URL="https://github.com/sourcefrog/cargo-mutants/releases/download/v27.1.0/cargo-mutants-x86_64-unknown-linux-gnu.tar.gz"
    curl -sSfL "$CARGO_MUTANTS_URL" | tar xz -C "$HOME/.cargo/bin"
    echo "cargo-mutants installed successfully to $HOME/.cargo/bin"
else
    echo "cargo-mutants is already installed: $(cargo mutants --version)"
fi

echo "=== Rust Mutation Testing Setup Complete ==="
echo "You can now run: bash courseProjectDocs/mutation-testing/run-cargo-mutants-wsl.sh"

