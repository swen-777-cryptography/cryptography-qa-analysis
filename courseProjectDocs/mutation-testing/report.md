# Mutation Testing Report

## Setup Configuration
- **Tool**: `mutmut` and `pytest-gremlins`
- **Component**: `src/cryptography/utils.py`
- **Config**: Added `mutmut` and `pytest-gremlins` to the `test` dependencies in `pyproject.toml`. Because `mutmut` and `cryptography` compilation require native Linux libraries (like OpenSSL and POSIX `fork()`), the execution is instructed to be run via Windows Subsystem for Linux (WSL). We configured `setup.cfg` to use `source_paths=src/cryptography/utils.py` and `pytest_add_cli_args_test_selection=tests/test_utils.py`, while adding `also_copy=src/` to ensure full module availability during test isolation.

## Initial Mutation Score
- **Mutants Generated**: 83
- **Mutants Killed**: 43 (7 explicitly failed tests, 36 timed out)
- **Mutants Survived**: 14 (specifically in `int_to_bytes` logic)
- **Untested**: 26
- **Mutation Score**: ~75.4% (Killed / (Generated - Untested))

## Newly Added Tests
**Test Added by Ivan T**:
- **Targeted Mutant**: `cryptography.utils.x_int_to_bytes__mutmut_16` and others within `int_to_bytes`.
- **Test File**: `tests/test_utils.py`
- **Test Code**:
```python
def test_int_to_bytes_correctness():
    assert cryptography.utils.int_to_bytes(0) == b'\x00'
    assert cryptography.utils.int_to_bytes(1) == b'\x01'
    assert cryptography.utils.int_to_bytes(255) == b'\xff'
    assert cryptography.utils.int_to_bytes(256) == b'\x01\x00'
    assert cryptography.utils.int_to_bytes(1, 2) == b'\x00\x01'
```
*Analysis*: Previously, `int_to_bytes` only had tests verifying that it raised exceptions on invalid arguments (like length 0). By explicitly testing the returned byte strings for different inputs (including edge cases like `0`), we successfully targeted the mathematical operations and fallback length calculations that mutants were modifying.

## Final Mutation Score
- **Mutants Killed**: 28
- **Mutants Survived**: 29
- **Untested**: 26
- **Mutation Score**: ~49.1% (28 / (83 - 26))
*(Note: After correcting the `pytest` OpenSSL startup overhead by isolating tests with `forkserver`, 17 of the 18 mutants in `int_to_bytes` were successfully killed by our new test assertions. The only surviving mutant, #9, drops the `"big"` argument from `integer.to_bytes()`. Because Python 3.11+ defaults to `byteorder="big"`, this is an "equivalent mutant" whose behavior is mathematically identical to the original code, making it impossible to kill!)*

## Group Contributions
- [Group Member 1]: Set up the mutation testing framework (`mutmut` in WSL), documented instructions, and created the initial report template.
- [Group Member 2]: ...

