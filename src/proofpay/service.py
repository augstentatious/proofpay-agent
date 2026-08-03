"""Custody-minimized committed delivery service."""

from pathlib import Path
from secrets import token_bytes
from uuid import uuid4

from .crypto import digest, open_seal, seal, write_private
from .models import Invoice, PaymentEvidence, ProofPayConfig, ProofPayError, ReleasedArtifact
from .payment import payment_matches
from .policy import parse_amount, resolve_artifact
from .solana import b58encode, solana_pay_uri, validate_pubkey
from .store import InvoiceStore


class ProofPayService:
    def __init__(self, config: ProofPayConfig):
        validate_pubkey(config.recipient)
        validate_pubkey(config.token_mint)
        config.artifact_root.mkdir(parents=True, exist_ok=True)
        config.encrypted_root.mkdir(parents=True, exist_ok=True)
        config.release_root.mkdir(parents=True, exist_ok=True)
        self.config = config
        self.store = InvoiceStore(config.state_db)

    def create_invoice(self, artifact_name: str, amount: str, buyer_label: str) -> Invoice:
        artifact = resolve_artifact(self.config, artifact_name)
        value = parse_amount(self.config, amount)
        if not buyer_label.strip() or len(buyer_label) > 120:
            raise ProofPayError("buyer label must be 1-120 characters")
        invoice_id = str(uuid4())
        reference = b58encode(token_bytes(32))
        plaintext = artifact.read_bytes()
        ciphertext, key = seal(plaintext, invoice_id)
        encrypted_path = self.config.encrypted_root / f"{invoice_id}.proofpay"
        write_private(encrypted_path, ciphertext)
        invoice = Invoice(
            invoice_id=invoice_id,
            artifact_name=artifact.relative_to(self.config.artifact_root.resolve()).as_posix(),
            buyer_label=buyer_label.strip(),
            amount=value,
            recipient=self.config.recipient,
            token_mint=self.config.token_mint,
            token_decimals=self.config.token_decimals,
            reference=reference,
            pay_uri=solana_pay_uri(self.config.recipient, self.config.token_mint, value, reference),
            encrypted_path=encrypted_path,
            plaintext_sha256=digest(plaintext),
            ciphertext_sha256=digest(ciphertext),
        )
        self.store.save(invoice, key)
        artifact.unlink()
        return invoice

    def get_invoice(self, invoice_id: str) -> Invoice:
        invoice, _ = self.store.get(invoice_id)
        return invoice

    def record_payment(self, invoice_id: str, evidence: PaymentEvidence) -> bool:
        invoice, _ = self.store.get(invoice_id)
        if invoice.status == "paid":
            return invoice.signature == evidence.signature
        if not payment_matches(invoice, evidence):
            return False
        self.store.mark_paid(invoice_id, evidence.signature)
        return True

    def poll_payment(self, invoice_id: str, rpc) -> bool:
        invoice, _ = self.store.get(invoice_id)
        evidence = rpc.find_payment(invoice)
        return evidence is not None and self.record_payment(invoice_id, evidence)

    def release(self, invoice_id: str) -> ReleasedArtifact:
        invoice, key = self.store.get(invoice_id)
        if invoice.status != "paid":
            raise ProofPayError("invoice is not paid")
        plaintext = open_seal(invoice.encrypted_path.read_bytes(), key, invoice_id)
        if digest(plaintext) != invoice.plaintext_sha256:
            raise ProofPayError("artifact integrity check failed")
        safe_name = Path(invoice.artifact_name).name
        path = self.config.release_root / f"{invoice_id}-{safe_name}"
        write_private(path, plaintext)
        return ReleasedArtifact(invoice_id=invoice_id, path=path, sha256=digest(plaintext))
