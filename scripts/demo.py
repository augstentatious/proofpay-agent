#!/usr/bin/env python3
"""Local end-to-end demonstration using labeled synthetic chain evidence."""

import argparse
import json
from decimal import Decimal
from pathlib import Path

from proofpay.core import PaymentEvidence, ProofPayConfig, ProofPayError, ProofPayService

RECIPIENT = "11111111111111111111111111111111"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"


def token_balance(index, amount):
    return {
        "accountIndex": index,
        "mint": USDC,
        "owner": RECIPIENT,
        "uiTokenAmount": {"amount": str(amount), "decimals": 6},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    root = args.workdir.resolve()
    if root.exists():
        raise SystemExit(f"refusing to overwrite existing demo directory: {root}")
    artifacts = root / "artifacts"
    artifacts.mkdir(parents=True)
    (artifacts / "analysis.md").write_text("ProofPay verified deliverable\n")
    service = ProofPayService(ProofPayConfig(
        artifact_root=artifacts,
        encrypted_root=root / "sealed",
        release_root=root / "released",
        state_db=root / "state" / "proofpay.sqlite3",
        recipient=RECIPIENT,
        token_mint=USDC,
        token_decimals=6,
        max_amount=Decimal("1000"),
    ))
    invoice = service.create_invoice("analysis.md", "12.50", "demo-buyer")
    blocked_before_payment = False
    try:
        service.release(invoice.invoice_id)
    except ProofPayError:
        blocked_before_payment = True
    tx = {
        "meta": {
            "err": None,
            "preTokenBalances": [token_balance(2, 1_000_000)],
            "postTokenBalances": [token_balance(2, 13_500_000)],
        },
        "transaction": {"message": {"accountKeys": [invoice.reference, RECIPIENT]}},
    }
    accepted = service.record_payment(
        invoice.invoice_id,
        PaymentEvidence("SYNTHETIC_DEMO_SIGNATURE", "finalized", tx),
    )
    released = service.release(invoice.invoice_id)
    result = {
        "evidence": "synthetic fixture; no mainnet payment claimed",
        "invoice_id": invoice.invoice_id,
        "pay_uri": invoice.pay_uri,
        "blocked_before_payment": blocked_before_payment,
        "payment_accepted": accepted,
        "plaintext_sha256": invoice.plaintext_sha256,
        "ciphertext_sha256": invoice.ciphertext_sha256,
        "released": released.to_public_dict(),
        "released_text": released.path.read_text(),
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(rendered + "\n")
    print(rendered)


if __name__ == "__main__":
    main()
