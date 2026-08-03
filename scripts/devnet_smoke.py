#!/usr/bin/env python3
"""Create and settle a real ProofPay invoice on Solana devnet."""

import argparse
import json
import time
from decimal import Decimal
from pathlib import Path

from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.message import Message
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solana.rpc.api import Client
from solana.rpc.commitment import Finalized
from solana.rpc.types import TxOpts
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import TransferCheckedParams, transfer_checked

from proofpay.core import ProofPayConfig, ProofPayService
from proofpay.rpc import SolanaRpc

RPC = "https://api.devnet.solana.com"


def confirm(client, signature):
    result = client.confirm_transaction(signature, commitment=Finalized, sleep_seconds=1)
    if not result.value[0] or result.value[0].err is not None:
        raise RuntimeError(f"transaction failed: {signature}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--payer-keypair", type=Path, required=True)
    args = parser.parse_args()
    root = args.workdir.resolve()
    if root.exists():
        raise SystemExit(f"refusing to overwrite: {root}")
    artifacts = root / "artifacts"
    artifacts.mkdir(parents=True)
    (artifacts / "devnet-report.md").write_text("Explorer-verified ProofPay delivery\n")

    client = Client(RPC)
    key_bytes = bytes(json.loads(args.payer_keypair.read_text()))
    payer, recipient = Keypair.from_bytes(key_bytes), Keypair()
    balance = client.get_balance(payer.pubkey(), Finalized).value
    if balance < 10_000_000:
        raise RuntimeError(f"payer needs at least 0.01 devnet SOL; balance={balance}")
    token = Token.create_mint(client, payer, payer.pubkey(), 6, TOKEN_PROGRAM_ID)
    source = token.create_account(payer.pubkey())
    destination = token.create_account(recipient.pubkey())
    confirm(client, token.mint_to(source, payer, 2_000_000).value)

    service = ProofPayService(ProofPayConfig(
        artifact_root=artifacts,
        encrypted_root=root / "sealed",
        release_root=root / "released",
        state_db=root / "state" / "proofpay.sqlite3",
        recipient=str(recipient.pubkey()),
        token_mint=str(token.pubkey),
        token_decimals=6,
        max_amount=Decimal("10"),
    ))
    invoice = service.create_invoice("devnet-report.md", "1.25", "devnet-buyer")
    base = transfer_checked(TransferCheckedParams(
        TOKEN_PROGRAM_ID, source, token.pubkey, destination, payer.pubkey(), 1_250_000, 6
    ))
    referenced = Instruction(base.program_id, base.data, list(base.accounts) + [
        AccountMeta(Pubkey.from_string(invoice.reference), False, False)
    ])
    blockhash = client.get_latest_blockhash(Finalized).value.blockhash
    message = Message.new_with_blockhash([referenced], payer.pubkey(), blockhash)
    signature = client.send_transaction(Transaction([payer], message, blockhash), TxOpts()).value
    confirm(client, signature)

    rpc = SolanaRpc(RPC)
    paid = False
    for _ in range(20):
        if service.poll_payment(invoice.invoice_id, rpc):
            paid = True
            break
        time.sleep(2)
    if not paid:
        raise RuntimeError("finalized referenced payment was not detected")
    released = service.release(invoice.invoice_id)
    receipt = {
        "cluster": "devnet", "invoice_id": invoice.invoice_id,
        "mint": str(token.pubkey), "recipient": str(recipient.pubkey()),
        "reference": invoice.reference, "amount": str(invoice.amount),
        "signature": str(signature),
        "explorer": f"https://explorer.solana.com/tx/{signature}?cluster=devnet",
        "plaintext_sha256": invoice.plaintext_sha256,
        "ciphertext_sha256": invoice.ciphertext_sha256,
        "released_sha256": released.sha256,
        "source_removed": not (artifacts / "devnet-report.md").exists(),
        "payer_key_in_zeroclaw": False,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
