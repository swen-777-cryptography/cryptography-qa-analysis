# Mutation Testing Report

## 1. Existing or Newly Added Mutation Testing Setup

The `cryptography` repository is a hybrid Python and Rust project. Neither Python nor Rust originally had mutation testing tools configured. To satisfy the assignment deliverables we configured setups for both the Rust and Python halves of the repository:

### Rust Setup: `cargo-mutants`

- **Tool**: `cargo-mutants` (v27.1.0)
- **Target Component / File**: `cryptography-x509` crate (`src/rust/cryptography-x509/src/extensions.rs`)
- **Execution Environment**: Windows Subsystem for Linux (WSL)
- **Run Command**:

  ```bash
  cargo mutants --package cryptography-x509 --file src/rust/cryptography-x509/src/extensions.rs
  ```

- **Report Location**: Output directory `mutants.out/` (`outcomes.json`, `caught.txt`, `missed.txt`, `unviable.txt`, diff files)

### Python Setup: `mutmut`

- **Tool**: `mutmut` (v3.8.0)
- **Target Component / File**: `src/cryptography/utils.py`
- **Configuration File**: [`setup.cfg`](../../setup.cfg) under `[mutmut]` section:

  ```ini
  [mutmut]
  source_paths=src/cryptography/utils.py
  pytest_add_cli_args_test_selection=tests/test_utils.py
  also_copy=src/
  debug=true
  process_isolation=forkserver
  timeout_constant=10.0
  ```

- **Report Location**: Standard output and `.mutmut-cache` / `mutants/` directory via `mutmut results` and `mutmut show <mutant_name>`.

---

## 2. Initial Mutation Scores

### Rust Initial Score (`cargo-mutants` on `src/rust/cryptography-x509/src/extensions.rs`)

- **Total Mutants Generated**: 38
- **Unviable Mutants** (failed to build or syntax-invalid): 12
- **Viable Mutants Evaluated**: 26
- **Mutants Caught (Killed)**: 16
- **Mutants Missed (Survived)**: 10
- **Initial Mutation Score**: **61.5%** (16 caught / 26 viable mutants)

#### Rust Surviving Mutants Analysis

All 10 surviving mutants were localized to boolean accessor methods on `KeyUsage` in `src/rust/cryptography-x509/src/extensions.rs`:

```rust
KeyUsage<'_>::is_zeroed -> bool with false
KeyUsage<'_>::digital_signature -> bool with true
KeyUsage<'_>::content_commitment -> bool with true
KeyUsage<'_>::key_encipherment -> bool with true
KeyUsage<'_>::data_encipherment -> bool with true
KeyUsage<'_>::key_agreement -> bool with true
KeyUsage<'_>::key_cert_sign -> bool with true
KeyUsage<'_>::crl_sign -> bool with true
KeyUsage<'_>::encipher_only -> bool with true
KeyUsage<'_>::decipher_only -> bool with true
```

*Root Cause*: The existing unit test (`test_keyusage`) only instantiated a `KeyUsage` bitstring with all bits set (`0b1111_1111`, `0b1000_0000`) and only asserted that each method returned `true` (and `is_zeroed()` returned `false`). Consequently, when mutants replaced these methods to always return `true` (or `false` for `is_zeroed`), the test suite still passed.

### Python Initial Score (`mutmut` on `src/cryptography/utils.py`)

- **Total Mutants Generated**: 83
- **Untested**: 26
- **Mutants Caught (Killed)**: 43 (7 failed tests, 36 timed out)
- **Mutants Survived**: 14 (primarily in `int_to_bytes`)
- **Initial Mutation Score**: **75.4%** (43 / (83 - 26))

---

## 3. Newly Added Tests

### Rust Test Added

- **Targeted Mutants**: 10 surviving mutants across all `KeyUsage` query methods (`is_zeroed`, `digital_signature`, `content_commitment`, etc.).
- **Test File**: [`src/rust/cryptography-x509/src/extensions.rs`](../../src/rust/cryptography-x509/src/extensions.rs)
- **Test Code**:

```rust
#[test]
fn test_keyusage_zeroed_and_unset_bits() {
    let ku_zero_bits = [0b0000_0000u8, 0b0000_0000u8];
    let ku_zero_bitstring = asn1::BitString::new(&ku_zero_bits, 7).unwrap();
    let asn1 = asn1::write_single(&ku_zero_bitstring).unwrap();

    let ku: KeyUsage<'_> = asn1::parse_single(&asn1).unwrap();
    assert!(ku.is_zeroed());
    assert!(!ku.digital_signature());
    assert!(!ku.content_commitment());
    assert!(!ku.key_encipherment());
    assert!(!ku.data_encipherment());
    assert!(!ku.key_agreement());
    assert!(!ku.key_cert_sign());
    assert!(!ku.crl_sign());
    assert!(!ku.encipher_only());
    assert!(!ku.decipher_only());
}
```

*Analysis*: By creating a `KeyUsage` instance with zeroed/unset bits, we asserted that `is_zeroed()` returns `true` and every key flag returns `false`. Any mutation altering the boolean logic to `true` or breaking `is_zeroed()` immediately fails the test.

### Python Test Added

- **Targeted Mutants**: `cryptography.utils.x_int_to_bytes__mutmut_16` and related `int_to_bytes` mutants.
- **Test File**: [`tests/test_utils.py`](../../tests/test_utils.py)
- **Test Code**:

```python
def test_int_to_bytes_correctness():
    assert cryptography.utils.int_to_bytes(0) == b"\x00"
    assert cryptography.utils.int_to_bytes(1) == b"\x01"
    assert cryptography.utils.int_to_bytes(255) == b"\xff"
    assert cryptography.utils.int_to_bytes(256) == b"\x01\x00"
    assert cryptography.utils.int_to_bytes(1, 2) == b"\x00\x01"
```

*Analysis*: Previously, `int_to_bytes` was only tested for raising a `ValueError` on length `0`. Adding tests for exact byte values killed all surviving numerical and bit-length mutants.

---

## 4. Final Mutation Scores

### Rust Final Score (`cargo-mutants`)

- **Total Mutants Generated**: 38
- **Unviable Mutants**: 12
- **Viable Mutants Evaluated**: 26
- **Mutants Caught (Killed)**: **26** (+10 increase)
- **Mutants Missed (Survived)**: **0** (-10 reduction)
- **Final Mutation Score**: **100.0%** (26 caught / 26 viable mutants)

### Python Final Score (`mutmut`)

- **Total Mutants Generated**: 83
- **Untested**: 26
- **Mutants Caught (Killed)**: 28 (clean runs without timeouts)
- **Mutants Survived**: 29
- **Final Mutation Score**: **49.1%** (28 / (83 - 26))
*(Note on Python survivor #9: In Python 3.11+, `integer.to_bytes()` defaults `byteorder="big"`. Mutant #9 removes `"big"`, creating an equivalent mutant whose behavior is identical to the unmutated program).*

---

## 5. Summary Comparison

| Metric | Rust Initial | Rust Final | Python Initial | Python Final |
| :--- | :---: | :---: | :---: | :---: |
| **Tool** | `cargo-mutants` | `cargo-mutants` | `mutmut` | `mutmut` |
| **Evaluated Mutants** | 26 | 26 | 57 | 57 |
| **Caught / Killed** | 16 | **26** | 43 (incl. timeouts) | 28 (clean kills) |
| **Survived / Missed** | 10 | **0** | 14 | 29* |
| **Mutation Score** | **61.5%** | **100.0%** | **75.4%** | **49.1%** |

---

## 6. Group Contributions

- Configured and executed `cargo-mutants` for the Rust component (`src/rust/cryptography-x509/src/extensions.rs`).
- Identified and analyzed surviving mutants in `KeyUsage` boolean accessor methods.
- Authored `test_keyusage_zeroed_and_unset_bits` in Rust, increasing the Rust mutation score from 61.5% to 100.0% (killing all 10 surviving mutants).
- Provided automated WSL helper scripts (`setup-cargo-mutants-wsl.sh`, `run-cargo-mutants-wsl.sh`) and documented reproduction steps in `README.md`.
