# Integration tests for Fernet based on https://cryptography.io/en/latest/fernet/

import base64
import os

import pytest

from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derive_fernet_key(password: bytes, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password and salt using PBKDF2HMAC."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1_200_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password))


def test_fernet_with_password_kdf():
    """Using passwords with Fernet: PBKDF2HMAC + SHA256 + Fernet."""
    password = b"password"
    salt = os.urandom(16)
    message = b"Secret message!"

    key = derive_fernet_key(password, salt)
    f = Fernet(key)
    token = f.encrypt(message)

    # Same password + salt decrypts successfully
    decrypt_key = derive_fernet_key(password, salt)
    assert Fernet(decrypt_key).decrypt(token) == message

    # Wrong password fails with InvalidToken
    wrong_key = derive_fernet_key(b"wrong-password", salt)
    with pytest.raises(InvalidToken):
        Fernet(wrong_key).decrypt(token)


def test_multifernet_key_rotation():
    """Key rotation with MultiFernet: Fernet + MultiFernet."""
    old_key = Fernet.generate_key()
    new_key = Fernet.generate_key()
    message = b"Secret message!"

    f_old = Fernet(old_key)
    f_new = Fernet(new_key)

    # Encrypt with the old key, then rotate using MultiFernet
    old_token = f_old.encrypt(message)
    multi = MultiFernet([f_new, f_old])
    assert multi.decrypt(old_token) == message

    rotated_token = multi.rotate(old_token)
    assert f_new.decrypt(rotated_token) == message

    # Old key can no longer decrypt after rotation
    with pytest.raises(InvalidToken):
        f_old.decrypt(rotated_token)
