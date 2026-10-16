# Python Mutation Testing Report (`mutmut`)

## 1. Overview & Setup

Mutation testing was conducted on the Python components of the `cryptography` library using `mutmut`. Because of the project's scale, mutation testing was targeted on the core utility module:
- **Target Source File**: [`src/cryptography/utils.py`](../../src/cryptography/utils.py)
- **Target Test File**: [`tests/test_utils.py`](../../tests/test_utils.py)

---

## 2. Initial Mutation Score

Upon running `mutmut run` on `src/cryptography/utils.py` against the initial test suite, a substantial number of mutants either survived or were completely untested:

- **Total Mutants Generated**: 83
- **Mutants Killed (Caught)**: 28
- **Mutants Survived (Missed)**: 29
- **Untested Mutants (No Tests)**: 26
- **Initial Mutation Score**:
  - **33.7%** overall (28 killed / 83 total generated)
  - **49.1%** covered (28 killed / 57 covered mutants)

---

## 3. Analysis of Surviving & Untested Mutants

Analysis of the 55 non-killed mutants (29 survived + 26 untested) revealed several distinct gaps in test coverage:

### A. `int_to_bytes` (1 mutant survived)
* **Target Mutant**: `cryptography.utils.x_int_to_bytes__mutmut_9`
* **Mutation**: Removed the `"big"` byteorder parameter from `integer.to_bytes(...)`:
  ```python
  - return integer.to_bytes(length or (integer.bit_length() + 7) // 8 or 1, "big")
  + return integer.to_bytes(length or (integer.bit_length() + 7) // 8 or 1, )
  ```
* **Analysis**: In Python 3.11+, `int.to_bytes(length, byteorder="big")` defaults `byteorder` to `"big"`. Passing standard integers caused this mutation to act as an equivalent mutant. To kill this mutant, an `int` subclass that requires an explicit byteorder argument was needed.

### B. `_check_bytes` (2 mutants untested)
* **Target Mutants**: `x__check_bytes__mutmut_1`, `mutmut_2`
* **Mutation**: Inverted check to `if isinstance(value, bytes): raise TypeError` and replaced exception message with `None`.
* **Analysis**: `_check_bytes` was never called directly by unit tests in `tests/test_utils.py`.

### C. `_check_byteslike` (2 mutants untested)
* **Target Mutants**: `x__check_byteslike__mutmut_1`, `mutmut_2`
* **Mutation**: Mutated `memoryview(value)` to `memoryview(None)` and exception message to `None`.
* **Analysis**: `_check_byteslike` was never directly tested, especially with buffer-protocol objects that are not `(bytes, bytearray, memoryview)` (such as `array.array`), which are required to exercise the fallback `try: memoryview(value)` branch.

### D. `_DeprecatedValue` (3 mutants survived)
* **Target Mutants**: `xǁ_DeprecatedValueǁ__init____mutmut_1` to `mutmut_3`
* **Mutation**: Nullified attributes upon initialization (`self.value = None`, `self.message = None`, `self.warning_class = None`).
* **Analysis**: The fields were never directly verified after instantiation.

### E. `_ModuleWithDeprecations` (29 mutants survived / untested)
* **`__init__` (4 mutants survived)**: `super().__init__(None)` and dictionary corruption (`self.__dict__["_module"] = None`, `"XX_moduleXX"`, `"_MODULE"`). `__name__` and `_module` attributes were never asserted.
* **`__getattr__` (3 mutants survived)**: Emitted `None` as warning message (`mutmut_6`), omitted `stacklevel=2` (`mutmut_11`), or changed to `stacklevel=3` (`mutmut_12`). The existing test only used `pytest.warns(DeprecationWarning)` without verifying message string or caller stacklevel attribution.
* **`__delattr__` (19 mutants untested)**: Entire method lacked test coverage. Mutants corrupted `getattr()`, stripped `warnings.warn` parameters, omitted the default fallback parameter in `self.__dict__.pop(attr, None)` (which causes `KeyError` on uncached attributes), and corrupted `delattr()`.
* **`__dir__` (3 mutants untested)**: Mutated `"_module"` to `"XX_moduleXX"`, `"_MODULE"`, or `dir(None)`. The `dir()` representation of wrapped modules was never tested.

### F. `deprecated()` Function (18 mutants survived)
* **Target Mutants**: `x_deprecated__mutmut_1` to `mutmut_18`
* **Mutation**: Bypassed module wrapping checks, corrupted module dictionary updates, dropped `_DeprecatedValue` arguments, and inverted `if name is not None:`.
* **Analysis**: `deprecated()` was only executed at module import time inside `tests/deprecated_module.py`. Because it was never called dynamically within test cases, mutmut could not isolate tests to verify module wrapping, re-wrapping prevention, or backwards compatibility with `name=None`.

---

## 4. Newly Added Tests

All new tests were added to [`tests/test_utils.py`](../../tests/test_utils.py):

### 1. Enforcing Explicit Big-Endian Byte Order
Kills `x_int_to_bytes__mutmut_9`:
```python
def test_int_to_bytes_explicit_big_endian():
    class StrictBigEndianInt(int):
        def to_bytes(self, *args, **kwargs):
            if len(args) < 2 or args[1] != "big":
                raise ValueError("explicit 'big' byteorder required")
            return super().to_bytes(*args, **kwargs)

    assert cryptography.utils.int_to_bytes(StrictBigEndianInt(1)) == b"\x01"
    assert (
        cryptography.utils.int_to_bytes(StrictBigEndianInt(256), 2)
        == b"\x01\x00"
    )
```

### 2. Validating `_check_bytes` and `_check_byteslike`
Kills `_check_bytes` mutants 1–2 and `_check_byteslike` mutants 1–2:
```python
def test_check_bytes():
    cryptography.utils._check_bytes("test_bytes", b"valid")
    with pytest.raises(TypeError, match=r"^test_bytes must be bytes$"):
        cryptography.utils._check_bytes("test_bytes", "invalid_str")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match=r"^other_name must be bytes$"):
        cryptography.utils._check_bytes("other_name", 123)  # type: ignore[arg-type]


def test_check_byteslike():
    cryptography.utils._check_byteslike("buf", b"bytes")
    cryptography.utils._check_byteslike("buf", bytearray(b"bytearray"))
    cryptography.utils._check_byteslike("buf", memoryview(b"memview"))
    # array.array supports the buffer protocol but is not bytes,
    # bytearray, or memoryview
    arr = array.array("B", b"array_buffer")
    cryptography.utils._check_byteslike("buf", arr)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match=r"^buf must be bytes-like$"):
        cryptography.utils._check_byteslike("buf", "not_buffer")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match=r"^other must be bytes-like$"):
        cryptography.utils._check_byteslike("other", 12345)  # type: ignore[arg-type]
```

### 3. Testing `_DeprecatedValue` Initialization
Kills `_DeprecatedValue` mutants 1–3:
```python
def test_deprecated_value(self):
    dv = cryptography.utils._DeprecatedValue(
        "val", "warning_msg", DeprecationWarning
    )
    assert dv.value == "val"
    assert dv.message == "warning_msg"
    assert dv.warning_class is DeprecationWarning
```

### 4. Testing `_ModuleWithDeprecations` Behavior
Kills `_ModuleWithDeprecations` mutants across `__init__`, `__getattr__`, `__delattr__`, and `__dir__`:
```python
def test_module_with_deprecations_init(self):
    mod = types.ModuleType("custom_mod")
    wrapped = cryptography.utils._ModuleWithDeprecations(mod)
    assert wrapped.__name__ == "custom_mod"
    assert wrapped._module is mod
    assert wrapped.__dict__["_module"] is mod
    assert "XX_moduleXX" not in wrapped.__dict__
    assert "_MODULE" not in wrapped.__dict__


def test_module_with_deprecations_getattr_warning_details(
    self, monkeypatch
):
    mod = types.ModuleType("dummy_getattr")
    wrapped = cryptography.utils._ModuleWithDeprecations(mod)
    dv = cryptography.utils._DeprecatedValue(
        42, "msg_getattr", DeprecationWarning
    )
    setattr(mod, "DEP", dv)

    warn_calls = []
    monkeypatch.setattr(
        warnings,
        "warn",
        lambda *args, **kwargs: warn_calls.append((args, kwargs)),
    )

    val = wrapped.DEP
    assert val == 42
    assert len(warn_calls) == 1
    args, kwargs = warn_calls[0]
    assert args == ("msg_getattr", DeprecationWarning)
    assert kwargs == {"stacklevel": 2}


def test_module_with_deprecations_delattr(self, monkeypatch):
    mod = types.ModuleType("dummy_delattr")
    wrapped = cryptography.utils._ModuleWithDeprecations(mod)

    # 1. Deleting a deprecated attribute emits warning with exact details
    dv = cryptography.utils._DeprecatedValue(
        99, "del_dep_msg", DeprecationWarning
    )
    setattr(mod, "DEP_ATTR", dv)
    assert hasattr(mod, "DEP_ATTR")

    warn_calls = []
    monkeypatch.setattr(
        warnings,
        "warn",
        lambda *args, **kwargs: warn_calls.append((args, kwargs)),
    )

    del wrapped.DEP_ATTR
    assert len(warn_calls) == 1
    args, kwargs = warn_calls[0]
    assert args == ("del_dep_msg", DeprecationWarning)
    assert kwargs == {"stacklevel": 2}
    assert not hasattr(mod, "DEP_ATTR")
    assert not hasattr(wrapped, "DEP_ATTR")
    assert "DEP_ATTR" not in wrapped.__dict__

    # 2. Deleting a normal attribute that was cached in wrapped.__dict__
    setattr(mod, "CACHED", "cached_val")
    assert wrapped.CACHED == "cached_val"
    assert "CACHED" in wrapped.__dict__
    del wrapped.CACHED
    assert "CACHED" not in wrapped.__dict__
    assert not hasattr(mod, "CACHED")
    assert not hasattr(wrapped, "CACHED")

    # 3. Deleting a normal attribute that was NOT in wrapped.__dict__
    setattr(mod, "UNCACHED", "uncached_val")
    assert "UNCACHED" not in wrapped.__dict__
    del wrapped.UNCACHED
    assert not hasattr(mod, "UNCACHED")
    assert not hasattr(wrapped, "UNCACHED")

    # 4. Deleting a non-existent attribute raises AttributeError
    with pytest.raises(AttributeError):
        del wrapped.NON_EXISTENT


def test_module_with_deprecations_dir(self):
    mod = types.ModuleType("dummy_dir")
    setattr(mod, "custom_attr", 10)
    wrapped = cryptography.utils._ModuleWithDeprecations(mod)
    assert wrapped.__dir__() == ["_module", *dir(mod)]
    assert dir(wrapped) == sorted(["_module", *dir(mod)])
    assert "XX_moduleXX" not in dir(wrapped)
    assert "_MODULE" not in dir(wrapped)
```

### 5. Testing the `deprecated()` Function Directly
Kills all 18 `deprecated()` mutants:
```python
def test_deprecated_function(self, monkeypatch):
    mod_name = "test_custom_deprecated_mod"
    mod = types.ModuleType(mod_name)
    monkeypatch.setitem(sys.modules, mod_name, mod)

    # First call wraps module into _ModuleWithDeprecations and registers
    # deprecated attr
    dv = cryptography.utils.deprecated(
        value=123,
        module_name=mod_name,
        message="123 is deprecated",
        warning_class=DeprecationWarning,
        name="OLD_ATTR",
    )
    assert isinstance(dv, cryptography.utils._DeprecatedValue)
    assert dv.value == 123
    assert dv.message == "123 is deprecated"
    assert dv.warning_class is DeprecationWarning

    wrapped = sys.modules[mod_name]
    assert isinstance(wrapped, cryptography.utils._ModuleWithDeprecations)
    assert wrapped._module is mod
    assert getattr(mod, "OLD_ATTR") is dv

    with pytest.warns(DeprecationWarning, match=r"^123 is deprecated$"):
        assert wrapped.OLD_ATTR == 123

    # Second call on the SAME module should NOT re-wrap
    dv2 = cryptography.utils.deprecated(
        value=456,
        module_name=mod_name,
        message="456 is deprecated",
        warning_class=UserWarning,
        name="ANOTHER_ATTR",
    )
    assert sys.modules[mod_name] is wrapped
    assert getattr(mod, "ANOTHER_ATTR") is dv2
    with pytest.warns(UserWarning, match=r"^456 is deprecated$"):
        assert wrapped.ANOTHER_ATTR == 456

    # Call with name=None maintains backwards compatibility with pyOpenSSL
    mod_name_none = "test_custom_deprecated_mod_none"
    mod_none = types.ModuleType(mod_name_none)
    monkeypatch.setitem(sys.modules, mod_name_none, mod_none)

    dv_none = cryptography.utils.deprecated(
        value=789,
        module_name=mod_name_none,
        message="789 is deprecated",
        warning_class=DeprecationWarning,
        name=None,
    )
    assert isinstance(dv_none, cryptography.utils._DeprecatedValue)
    assert dv_none.value == 789
    assert not hasattr(mod_none, "None")
    assert not hasattr(sys.modules[mod_name_none], "None")
```

---

## 5. Final Mutation Score & Results Comparison

Re-running `courseProjectDocs/mutation-testing/run-mutmut-wsl.sh` after introducing the new tests killed every generated mutant:

### Summary Comparison Table

| Metric | Initial Score (`mutmut`) | Final Score (`mutmut`) | Change |
| :--- | :---: | :---: | :---: |
| **Total Mutants Generated** | 83 | 83 | — |
| **Untested Mutants (No Tests)** | 26 | **0** | **-26** |
| **Mutants Survived** | 29 | **0** | **-29** |
| **Mutants Caught (Killed)** | 28 | **83** | **+55** |
| **Mutation Score (Overall)** | **33.7%** (28 / 83) | **100.0%** (83 / 83) | **+66.3%** |
| **Mutation Score (Covered)** | **49.1%** (28 / 57) | **100.0%** (83 / 83) | **+50.9%** |

