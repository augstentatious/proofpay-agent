from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

from conftest import RECIPIENT, USDC_MINT
from proofpay.core import ProofPayError


def test_create_invoice_encrypts_and_locks_payment_policy(service):
    invoice = service.create_invoice("report.md", "50.25", "buyer-7")

    assert invoice.recipient == RECIPIENT
    assert invoice.token_mint == USDC_MINT
    assert invoice.amount == Decimal("50.25")
    assert invoice.encrypted_path.exists()
    assert not (service.config.artifact_root / "report.md").exists()
    assert invoice.encrypted_path.read_bytes() != b"verified deliverable\n"
    assert invoice.plaintext_sha256 == sha256(b"verified deliverable\n").hexdigest()
    assert "key" not in invoice.to_public_dict()

    parsed = urlparse(invoice.pay_uri)
    query = parse_qs(parsed.query)
    assert parsed.scheme == "solana"
    assert parsed.path == RECIPIENT
    assert query["spl-token"] == [USDC_MINT]
    assert query["amount"] == ["50.25"]
    assert query["reference"] == [invoice.reference]


def test_create_invoice_rejects_escape_and_amount_over_cap(service, tmp_path: Path):
    (tmp_path / "outside.txt").write_text("nope")
    with pytest.raises(ProofPayError, match="artifact root"):
        service.create_invoice("../outside.txt", "1", "buyer")
    with pytest.raises(ProofPayError, match="maximum"):
        service.create_invoice("report.md", "1000.000001", "buyer")
