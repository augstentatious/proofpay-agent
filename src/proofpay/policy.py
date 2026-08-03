"""Fail-closed input policy."""

from decimal import Decimal, InvalidOperation
from pathlib import Path

from .models import ProofPayConfig, ProofPayError


def resolve_artifact(config: ProofPayConfig, artifact_name: str) -> Path:
    if not artifact_name or Path(artifact_name).is_absolute():
        raise ProofPayError("artifact must be a relative path inside artifact root")
    root = config.artifact_root.resolve()
    candidate = (root / artifact_name).resolve()
    if not candidate.is_relative_to(root) or not candidate.is_file() or candidate.is_symlink():
        raise ProofPayError("artifact must resolve to a regular file inside artifact root")
    return candidate


def parse_amount(config: ProofPayConfig, raw: str) -> Decimal:
    try:
        amount = Decimal(raw)
    except InvalidOperation as exc:
        raise ProofPayError("invalid amount") from exc
    if not amount.is_finite() or amount <= 0:
        raise ProofPayError("amount must be positive and finite")
    quantum = Decimal(1).scaleb(-config.token_decimals)
    if amount.quantize(quantum) != amount:
        raise ProofPayError("amount exceeds token precision")
    if amount > config.max_amount:
        raise ProofPayError("amount exceeds operator maximum")
    return amount
