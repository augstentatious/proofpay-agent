"""Pure Solana payment-evidence evaluation."""

from decimal import Decimal
from typing import Any

from .models import Invoice, PaymentEvidence


def _pubkeys(transaction: dict[str, Any]) -> set[str]:
    keys = transaction.get("transaction", {}).get("message", {}).get("accountKeys", [])
    return {item if isinstance(item, str) else item.get("pubkey", "") for item in keys}


def _balances(entries: list[dict[str, Any]], invoice: Invoice) -> dict[int, int]:
    result: dict[int, int] = {}
    for entry in entries:
        if entry.get("mint") != invoice.token_mint or entry.get("owner") != invoice.recipient:
            continue
        amount = entry.get("uiTokenAmount", {}).get("amount")
        try:
            result[int(entry["accountIndex"])] = int(amount)
        except (KeyError, TypeError, ValueError):
            return {}
    return result


def payment_matches(invoice: Invoice, evidence: PaymentEvidence) -> bool:
    if evidence.confirmation_status != "finalized" or not evidence.signature:
        return False
    tx = evidence.transaction
    meta = tx.get("meta")
    if not isinstance(meta, dict) or meta.get("err") is not None:
        return False
    if invoice.reference not in _pubkeys(tx):
        return False
    pre = _balances(meta.get("preTokenBalances", []), invoice)
    post = _balances(meta.get("postTokenBalances", []), invoice)
    indices = set(pre) | set(post)
    credited = sum(post.get(index, 0) - pre.get(index, 0) for index in indices)
    expected = invoice.amount * (Decimal(10) ** invoice.token_decimals)
    return expected == expected.to_integral_value() and credited == int(expected)
