# Mutation Testing Setup and Execution

This directory documents the mutation testing setup for the `cryptography` project, covering Python (`mutmut`), but omitting Rust.

To run mutation testing on Windows, use **WSL** because the project's native build tools, OpenSSL linkages, and mutation test runners rely on POSIX process isolation.

---

## Python Mutation Testing (`mutmut`)

### 1. Overview

- **Tool**: `mutmut` (v3.8.0)
- **Target Component**: `src/cryptography/utils.py`
- **Configuration**: [`setup.cfg`](../../setup.cfg) under `[mutmut]` section.

### 2. Automated Scripts

1. **Setup Python Environment & Dependencies**:

   ```bash
   bash courseProjectDocs/mutation-testing/setup-mutmut.sh
   ```

   Provisions `.venv`, installs project build requirements, dependencies, and compiles the Rust extension via `maturin develop`.

2. **Run Python Mutation Tests**:

   ```bash
   bash courseProjectDocs/mutation-testing/run-mutmut.sh
   ```

3. **Inspect Python Mutants**:

   ```bash
   source .venv/bin/activate
   mutmut show <mutant-name>
   # e.g.: mutmut show cryptography.utils.x_int_to_bytes__mutmut_5
   ```
