"""Small Solana JSON-RPC client for invoice settlement checks."""

import json
from collections.abc import Callable
from urllib.request import Request, urlopen

from .models import Invoice, PaymentEvidence, ProofPayError
from .payment import payment_matches

Transport = Callable[[dict], dict]


class SolanaRpc:
    def __init__(self, url: str, transport: Transport | None = None):
        if not url.startswith("https://"):
            raise ProofPayError("RPC URL must use HTTPS")
        self.url = url
        self.transport = transport or self._post

    def _post(self, payload: dict) -> dict:
        request = Request(
            self.url,
            data=json.dumps(payload).encode(),
            headers={"content-type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=15) as response:
            return json.load(response)

    def _call(self, method: str, params: list) -> object:
        response = self.transport({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
        if not isinstance(response, dict) or response.get("error"):
            raise ProofPayError(f"Solana RPC {method} failed")
        return response.get("result")

    def find_payment(self, invoice: Invoice) -> PaymentEvidence | None:
        signatures = self._call(
            "getSignaturesForAddress",
            [invoice.reference, {"limit": 20, "commitment": "finalized"}],
        )
        if not isinstance(signatures, list):
            raise ProofPayError("invalid signature response")
        for item in signatures:
            if not isinstance(item, dict) or item.get("err") is not None:
                continue
            signature = item.get("signature")
            status = item.get("confirmationStatus")
            if not signature or status != "finalized":
                continue
            transaction = self._call(
                "getTransaction",
                [signature, {"encoding": "jsonParsed", "commitment": "finalized", "maxSupportedTransactionVersion": 0}],
            )
            if isinstance(transaction, dict):
                evidence = PaymentEvidence(signature, status, transaction)
                if payment_matches(invoice, evidence):
                    return evidence
        return None
