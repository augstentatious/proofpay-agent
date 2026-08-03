"""Authenticated encryption for committed artifacts."""

from hashlib import sha256
from pathlib import Path
from secrets import token_bytes

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .models import ProofPayError

_MAGIC = b"PROOFPAY1"


def seal(plaintext: bytes, invoice_id: str) -> tuple[bytes, bytes]:
    key = token_bytes(32)
    nonce = token_bytes(12)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, invoice_id.encode())
    return _MAGIC + nonce + ciphertext, key


def open_seal(blob: bytes, key: bytes, invoice_id: str) -> bytes:
    if not blob.startswith(_MAGIC) or len(blob) < len(_MAGIC) + 13:
        raise ProofPayError("artifact decryption failed")
    nonce = blob[len(_MAGIC) : len(_MAGIC) + 12]
    ciphertext = blob[len(_MAGIC) + 12 :]
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, invoice_id.encode())
    except InvalidTag as exc:
        raise ProofPayError("artifact decryption failed") from exc


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def write_private(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.chmod(0o600)
