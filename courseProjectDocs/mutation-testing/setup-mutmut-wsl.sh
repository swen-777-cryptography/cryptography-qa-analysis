#!/bin/bash
set -e

echo "=== Cryptography Mutmut WSL Setup ==="
echo "Updating apt and installing native dependencies (OpenSSL, Rust, Python dev headers)..."
sudo apt update
sudo apt install -y python3-venv python3-pip python3-dev libssl-dev pkg-config cargo rustc python3-maturin

echo "Creating isolated WSL virtual environment (.venv-wsl)..."
python3 -m venv .venv-wsl

echo "Activating virtual environment..."
source .venv-wsl/bin/activate

echo "Installing pip and uv..."
pip install -U pip uv

echo "Installing project and testing dependencies..."
uv pip install -e ./vectors
uv pip install ".[test,ssh]"

echo "Installing mutmut..."
uv pip install mutmut

echo "Building Rust bindings via maturin..."
maturin develop

echo "=== Setup Complete ==="
echo "You can now run: bash courseProjectDocs/mutation-testing/run-mutmut-wsl.sh"

