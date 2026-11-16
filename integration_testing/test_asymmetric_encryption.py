import datetime

import pytest

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import NameOID

NOW = datetime.datetime.now(datetime.timezone.utc)


@pytest.fixture(params=["rsa", "ec"])
def key(request):
    if request.param == "rsa":
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)
    else:
        return ec.generate_private_key(ec.SECP256R1())


def build_cert(subject_cn, issuer_cn, public_key, signing_key, ca=False):
    return (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject_cn)]))
        .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, issuer_cn)]))
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(NOW - datetime.timedelta(minutes=5))
        .not_valid_after(NOW + datetime.timedelta(days=30))
        .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True)
        .sign(signing_key, hashes.SHA256())
    )


def test_self_signed_cert_verifies(key):
    cert = build_cert("Test CA", "Test CA", key.public_key(), key, ca=True)
    cert.verify_directly_issued_by(cert)


def test_leaf_signed_by_ca(key):
    ca = build_cert("Test CA", "Test CA", key.public_key(), key, ca=True)
    leaf_key = ec.generate_private_key(ec.SECP256R1())
    leaf = build_cert("example.com", "Test CA", leaf_key.public_key(), key)
    leaf.verify_directly_issued_by(ca)


def test_leaf_rejected_by_wrong_ca(key):
    leaf = build_cert("example.com", "Test CA", key.public_key(), key)
    other_key = ec.generate_private_key(ec.SECP256R1())
    other_ca = build_cert(
        "Test CA", "Test CA", other_key.public_key(), other_key, ca=True
    )
    with pytest.raises(Exception):
        leaf.verify_directly_issued_by(other_ca)


def test_pem_roundtrip(key):
    cert = build_cert("Test CA", "Test CA", key.public_key(), key, ca=True)
    pem = cert.public_bytes(serialization.Encoding.PEM)
    assert x509.load_pem_x509_certificate(pem) == cert


def test_csr(key):
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "example.com")])
        )
        .sign(key, hashes.SHA256())
    )
    assert csr.is_signature_valid
