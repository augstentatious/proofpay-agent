"""SQLite state with secrets kept out of public model objects."""

import base64
import sqlite3
from decimal import Decimal
from pathlib import Path

from .models import Invoice, ProofPayError

_SCHEMA = """
CREATE TABLE IF NOT EXISTS invoices (
 invoice_id TEXT PRIMARY KEY, artifact_name TEXT NOT NULL, buyer_label TEXT NOT NULL,
 amount TEXT NOT NULL, recipient TEXT NOT NULL, token_mint TEXT NOT NULL,
 token_decimals INTEGER NOT NULL, reference TEXT NOT NULL, pay_uri TEXT NOT NULL,
 encrypted_path TEXT NOT NULL, plaintext_sha256 TEXT NOT NULL,
 ciphertext_sha256 TEXT NOT NULL, key_b64 TEXT NOT NULL,
 status TEXT NOT NULL, signature TEXT
)
"""


class InvoiceStore:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self._connect() as db:
            db.execute(_SCHEMA)
        path.chmod(0o600)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db

    def save(self, invoice: Invoice, key: bytes) -> None:
        values = invoice.to_public_dict()
        values["key_b64"] = base64.b64encode(key).decode()
        columns = list(values)
        query = f"INSERT INTO invoices ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})"
        with self._connect() as db:
            db.execute(query, [values[column] for column in columns])

    def get(self, invoice_id: str) -> tuple[Invoice, bytes]:
        with self._connect() as db:
            row = db.execute("SELECT * FROM invoices WHERE invoice_id = ?", (invoice_id,)).fetchone()
        if row is None:
            raise ProofPayError("unknown invoice")
        data = dict(row)
        key = base64.b64decode(data.pop("key_b64"), validate=True)
        data["amount"] = Decimal(data["amount"])
        data["encrypted_path"] = Path(data["encrypted_path"])
        return Invoice(**data), key

    def mark_paid(self, invoice_id: str, signature: str) -> None:
        with self._connect() as db:
            db.execute(
                "UPDATE invoices SET status = 'paid', signature = ? WHERE invoice_id = ? AND status = 'pending'",
                (signature, invoice_id),
            )
