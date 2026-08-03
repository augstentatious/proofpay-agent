"""Minimal Solana encoding helpers with no wallet dependency."""

from decimal import Decimal
from urllib.parse import urlencode

from .models import ProofPayError

_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_INDEX = {char: idx for idx, char in enumerate(_ALPHABET)}


def b58encode(raw: bytes) -> str:
    zeroes = len(raw) - len(raw.lstrip(b"\0"))
    number = int.from_bytes(raw, "big")
    encoded = ""
    while number:
        number, rem = divmod(number, 58)
        encoded = _ALPHABET[rem] + encoded
    return "1" * zeroes + encoded


def b58decode(text: str) -> bytes:
    number = 0
    try:
        for char in text:
            number = number * 58 + _INDEX[char]
    except KeyError as exc:
        raise ProofPayError("invalid Solana public key") from exc
    body = number.to_bytes((number.bit_length() + 7) // 8, "big") if number else b""
    return b"\0" * (len(text) - len(text.lstrip("1"))) + body


def validate_pubkey(value: str) -> str:
    if len(b58decode(value)) != 32:
        raise ProofPayError("invalid Solana public key")
    return value


def amount_text(amount: Decimal) -> str:
    return format(amount, "f").rstrip("0").rstrip(".") or "0"


def solana_pay_uri(recipient: str, mint: str, amount: Decimal, reference: str) -> str:
    query = urlencode(
        {
            "amount": amount_text(amount),
            "spl-token": mint,
            "reference": reference,
            "label": "ProofPay",
            "message": "Payment releases a committed digital deliverable",
        }
    )
    return f"solana:{recipient}?{query}"
