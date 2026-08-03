"""Operator-owned runtime configuration."""

import tomllib
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .models import ProofPayConfig, ProofPayError
from .rpc import SolanaRpc
from .service import ProofPayService

_REQUIRED = {
    "artifact_root",
    "encrypted_root",
    "release_root",
    "state_db",
    "recipient",
    "token_mint",
    "token_decimals",
    "max_amount",
    "rpc_url",
}


def load_runtime(path: Path) -> tuple[ProofPayService, SolanaRpc]:
    try:
        table = tomllib.loads(path.read_text()).get("proofpay", {})
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ProofPayError("invalid ProofPay config") from exc
    missing = sorted(_REQUIRED - set(table))
    if missing:
        raise ProofPayError(f"missing config fields: {', '.join(missing)}")
    try:
        config = ProofPayConfig(
            artifact_root=Path(table["artifact_root"]),
            encrypted_root=Path(table["encrypted_root"]),
            release_root=Path(table["release_root"]),
            state_db=Path(table["state_db"]),
            recipient=str(table["recipient"]),
            token_mint=str(table["token_mint"]),
            token_decimals=int(table["token_decimals"]),
            max_amount=Decimal(str(table["max_amount"])),
            max_inline_bytes=int(table.get("max_inline_bytes", 32768)),
        )
    except (TypeError, ValueError, InvalidOperation) as exc:
        raise ProofPayError("invalid ProofPay config value") from exc
    return ProofPayService(config), SolanaRpc(str(table["rpc_url"]))
