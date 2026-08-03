from decimal import Decimal
from hashlib import sha256

import pytest

from proofpay.core import PaymentEvidence, ProofPayError


def token_balance(index, mint, owner, amount):
    return {
        "accountIndex": index,
        "mint": mint,
        "owner": owner,
        "uiTokenAmount": {"amount": str(amount), "decimals": 6},
    }


def evidence(invoice, *, credited=50_250_000, reference=True, finalized=True):
    keys = [invoice.recipient]
    if reference:
        keys.append(invoice.reference)
    tx = {
        "meta": {
            "err": None,
            "preTokenBalances": [token_balance(0, invoice.token_mint, invoice.recipient, 0)],
            "postTokenBalances": [
                token_balance(0, invoice.token_mint, invoice.recipient, credited)
            ],
        },
        "transaction": {"message": {"accountKeys": keys}},
    }
    return PaymentEvidence(
        signature="sig-test",
        confirmation_status="finalized" if finalized else "confirmed",
        transaction=tx,
    )


def test_release_is_blocked_until_exact_finalized_payment(service):
    invoice = service.create_invoice("report.md", "50.25", "buyer-7")
    with pytest.raises(ProofPayError, match="not paid"):
        service.release(invoice.invoice_id)
    assert service.record_payment(invoice.invoice_id, evidence(invoice, reference=False)) is False
    assert service.record_payment(invoice.invoice_id, evidence(invoice, credited=1)) is False
    assert service.record_payment(invoice.invoice_id, evidence(invoice, finalized=False)) is False
    assert service.record_payment(invoice.invoice_id, evidence(invoice)) is True

    released = service.release(invoice.invoice_id)
    assert released.path.read_bytes() == b"verified deliverable\n"
    assert released.sha256 == sha256(b"verified deliverable\n").hexdigest()
    assert released.delivery_text == "verified deliverable\n"
    assert "key" not in released.to_public_dict()


def test_payment_for_wrong_mint_never_marks_paid(service):
    invoice = service.create_invoice("report.md", "50.25", "buyer-7")
    bad = evidence(invoice)
    bad.transaction["meta"]["postTokenBalances"][0]["mint"] = "11111111111111111111111111111111"
    assert service.record_payment(invoice.invoice_id, bad) is False
    assert service.get_invoice(invoice.invoice_id).status == "pending"


def test_tampered_ciphertext_never_releases_plaintext(service):
    invoice = service.create_invoice("report.md", "50.25", "buyer-7")
    assert service.record_payment(invoice.invoice_id, evidence(invoice)) is True
    blob = bytearray(invoice.encrypted_path.read_bytes())
    blob[-1] ^= 1
    invoice.encrypted_path.write_bytes(blob)
    with pytest.raises(ProofPayError, match="decrypt"):
        service.release(invoice.invoice_id)
