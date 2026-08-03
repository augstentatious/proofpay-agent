from proofpay.core import PaymentEvidence
from proofpay.rpc import SolanaRpc


def _balance(index, invoice, amount):
    return {
        "accountIndex": index,
        "mint": invoice.token_mint,
        "owner": invoice.recipient,
        "uiTokenAmount": {"amount": str(amount), "decimals": invoice.token_decimals},
    }


def test_rpc_finds_exact_finalized_reference_payment(service):
    invoice = service.create_invoice("report.md", "50.25", "buyer")
    calls = []

    def transport(payload):
        calls.append(payload)
        if payload["method"] == "getSignaturesForAddress":
            return {"result": [{"signature": "sig-1", "confirmationStatus": "finalized", "err": None}]}
        return {
            "result": {
                "meta": {
                    "err": None,
                    "preTokenBalances": [_balance(0, invoice, 0)],
                    "postTokenBalances": [_balance(0, invoice, 50_250_000)],
                },
                "transaction": {
                    "message": {"accountKeys": [invoice.recipient, invoice.reference]}
                },
            }
        }

    evidence = SolanaRpc("https://rpc.example", transport=transport).find_payment(invoice)
    assert isinstance(evidence, PaymentEvidence)
    assert evidence.signature == "sig-1"
    assert [call["method"] for call in calls] == ["getSignaturesForAddress", "getTransaction"]
    assert service.poll_payment(invoice.invoice_id, SolanaRpc("https://rpc.example", transport=transport))
    assert service.get_invoice(invoice.invoice_id).status == "paid"


def test_rpc_skips_reference_touch_and_finds_later_exact_payment(service):
    invoice = service.create_invoice("report.md", "50.25", "buyer")

    def transport(payload):
        if payload["method"] == "getSignaturesForAddress":
            return {"result": [
                {"signature": "touch", "confirmationStatus": "finalized", "err": None},
                {"signature": "payment", "confirmationStatus": "finalized", "err": None},
            ]}
        signature = payload["params"][0]
        credited = 1 if signature == "touch" else 50_250_000
        return {"result": {
            "meta": {"err": None, "preTokenBalances": [_balance(0, invoice, 0)],
                     "postTokenBalances": [_balance(0, invoice, credited)]},
            "transaction": {"message": {"accountKeys": [invoice.recipient, invoice.reference]}},
        }}

    evidence = SolanaRpc("https://rpc.example", transport=transport).find_payment(invoice)
    assert evidence.signature == "payment"
