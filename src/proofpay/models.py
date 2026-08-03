"""Public domain models for ProofPay."""

from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any


class ProofPayError(ValueError):
    """A fail-closed ProofPay policy or state error."""


@dataclass(frozen=True)
class ProofPayConfig:
    artifact_root: Path
    encrypted_root: Path
    release_root: Path
    state_db: Path
    recipient: str
    token_mint: str
    token_decimals: int
    max_amount: Decimal


@dataclass(frozen=True)
class Invoice:
    invoice_id: str
    artifact_name: str
    buyer_label: str
    amount: Decimal
    recipient: str
    token_mint: str
    token_decimals: int
    reference: str
    pay_uri: str
    encrypted_path: Path
    plaintext_sha256: str
    ciphertext_sha256: str
    status: str = "pending"
    signature: str | None = None

    def to_public_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["amount"] = str(self.amount)
        data["encrypted_path"] = str(self.encrypted_path)
        return data


@dataclass(frozen=True)
class PaymentEvidence:
    signature: str
    confirmation_status: str
    transaction: dict[str, Any]


@dataclass(frozen=True)
class ReleasedArtifact:
    invoice_id: str
    path: Path
    sha256: str

    def to_public_dict(self) -> dict[str, str]:
        return {"invoice_id": self.invoice_id, "path": str(self.path), "sha256": self.sha256}
