from decimal import Decimal
from pathlib import Path

import pytest

from proofpay.core import ProofPayConfig, ProofPayService

RECIPIENT = "11111111111111111111111111111111"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"


@pytest.fixture
def service(tmp_path: Path) -> ProofPayService:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    (artifacts / "report.md").write_text("verified deliverable\n")
    config = ProofPayConfig(
        artifact_root=artifacts,
        encrypted_root=tmp_path / "encrypted",
        release_root=tmp_path / "released",
        state_db=tmp_path / "proofpay.db",
        recipient=RECIPIENT,
        token_mint=USDC_MINT,
        token_decimals=6,
        max_amount=Decimal("1000"),
    )
    return ProofPayService(config)
