# Mutation Testing Setup and Execution

This directory documents the mutation testing setup for the `cryptography` project, covering both **Python** (`mutmut`) and **Rust** (`cargo-mutants`).

To run mutation testing on Windows, use **Windows Subsystem for Linux (WSL)** because the project's native build tools, OpenSSL linkages, and mutation test runners rely on POSIX process isolation and native C/Rust tooling.

---

## Part 1: Rust Mutation Testing (`cargo-mutants`)

### 1. Rust Overview

- **Tool**: [`cargo-mutants`](https://mutants.rs/) (v27.1.0)
- **Target Component**: `cryptography-x509` crate (`src/rust/cryptography-x509/src/extensions.rs`)
- **Report & Output Directory**: `mutants.out/` (generated during run: `outcomes.json`, `caught.txt`, `missed.txt`, `diff/`)

### 2. Rust Automated Scripts

1. **Setup `cargo-mutants`**:

   ```bash
   bash courseProjectDocs/mutation-testing/setup-cargo-mutants-wsl.sh
   ```

   This downloads and installs the prebuilt Linux binary for `cargo-mutants` into `~/.cargo/bin`.

2. **Run Rust Mutation Testing**:

   ```bash
   bash courseProjectDocs/mutation-testing/run-cargo-mutants-wsl.sh
   ```

   This clears old results and executes:

   ```bash
   cargo mutants --package cryptography-x509 --file src/rust/cryptography-x509/src/extensions.rs
   ```

3. **Inspect Mutants and Diffs**:
   The outcomes, logs, and exact diffs for each mutant are stored under `mutants.out/`:

   ```bash
   cat mutants.out/caught.txt
   cat mutants.out/missed.txt
   ls mutants.out/diff/
   ```

---

## Part 2: Python Mutation Testing (`mutmut`)

### 1. Python Overview

- **Tool**: `mutmut` (v3.8.0)
- **Target Component**: `src/cryptography/utils.py`
- **Configuration**: [`setup.cfg`](../../setup.cfg) under `[mutmut]` section.

### 2. Python Automated Scripts

1. **Setup Python Environment & Dependencies**:

   ```bash
   bash courseProjectDocs/mutation-testing/setup-mutmut-wsl.sh
   ```

   Provisions `.venv-wsl`, installs project build requirements, dependencies, and compiles the Rust extension via `maturin develop`.

2. **Run Python Mutation Tests**:

   ```bash
   bash courseProjectDocs/mutation-testing/run-mutmut-wsl.sh
   ```

3. **Inspect Python Mutants**:

   ```bash
   source .venv-wsl/bin/activate
   mutmut show <mutant-name>
   # e.g.: mutmut show cryptography.utils.x_int_to_bytes__mutmut_5
   ```
