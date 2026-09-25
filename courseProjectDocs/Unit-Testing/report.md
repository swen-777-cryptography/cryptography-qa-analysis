# Unit Testing I (Extend Coverage)

### Preface
The `cryptography` package already has incredibly high testing standards. The CI pipeline is configured to fail below *100%*, so opportunities to increase coverage are few and far between. That said, we did manage to find a few improvable areas.

### 1. BVA on Padding Block Sizes
By applying Boundary Value Analysis to the block size validation logic in the `PKCS7` padding implementation (`src/cryptography/hazmat/primitives/padding.py`), we identified the following bounds:

The block size validation checks two rules:
1. It must be in the range `[0, 2040]`.
2. It must be a multiple of 8.

However, only three arbitrary values (`127`, `4096`, `-2`) are included in the invalid parameter set. We added 5 specific boundary tests to ensure there are no off-by-one defects:

```python
    def test_bva_block_size_negative_one(self):
        """BVA: Just below the minimum valid range of 0"""
        with pytest.raises(ValueError):
            padding.PKCS7(-1)

    def test_bva_block_size_one(self):
        """BVA: Passes range check, but barely fails modulo 8 check"""
        with pytest.raises(ValueError):
            padding.PKCS7(1)

    def test_bva_block_size_2041(self):
        """BVA: Just above the maximum valid range of 2040"""
        with pytest.raises(ValueError):
            padding.PKCS7(2041)

    def test_bva_block_size_2048(self):
        """BVA: Fails range check, but passes modulo 8 check"""
        with pytest.raises(ValueError):
            padding.PKCS7(2048)

    def test_bva_block_size_seven(self):
        """BVA: One off from valid block size 8"""
        with pytest.raises(ValueError):
            padding.PKCS7(7)
```

### 2. Cryptographic Tampering and Edge-Case Logic
We also added 5 more tests across various cryptographic primitives to cover certain malformed/malicious inputs:

| Test Name | File | Rationale |
|-----------|------|-----------|
| `test_tampered_ciphertext_rejected` | `tests/test_fernet.py` | Encrypt data, flip one ciphertext byte, and assert `InvalidToken`. Ensures MAC validation catches data corruption. |
| `test_tampered_key_rejected` | `tests/test_fernet.py` | Encrypt with one Fernet key and confirm another key cannot decrypt it. Verifies key-binding uniqueness. |
| `test_sha256_known_empty_input` | `tests/hazmat/primitives/test_hashes.py` | Verify the empty-input (`b""`) SHA-256 digest against the standard known value. Checks the absolute lower-bound input for hashing. |
| `test_rsa_signature_rejects_modified_message` | `tests/hazmat/primitives/test_rsa.py` | Sign one message, verify against a different message, and assert `InvalidSignature`. Enforces strict signature validation. |
| `test_aes_gcm_rejects_modified_associated_data` | `tests/hazmat/primitives/test_aead.py` | Encrypt with AAD, then decrypt with altered AAD and assert `InvalidTag`. Validates authenticated encryption logic. |

## New Test Results

* **Total Tests Run**: 4,829 (previously 4,819 baseline)
  * **Python Tests**: 4,721
  * **Rust Tests**: 108
* **Passed**: 4,829
* **Failed**: 0

## Coverage Improvement Analysis

Our overall coverage remains at 100%, though in this case it would be concerning if adding new test cases impacted coverage.
