# ProofPay

ProofPay is a custody-minimized paid-delivery primitive for ZeroClaw. An agent can create a Solana Pay invoice, verify an exact finalized SPL-token payment, and release an AES-256-GCM sealed artifact.

The model never receives encryption keys and cannot choose the recipient, mint, RPC, file roots, token decimals, or amount ceiling. Those remain operator-owned TOML policy.

## MCP surface

- `proofpay__create_invoice(artifact_name, amount, buyer_label?)`
- `proofpay__invoice_status(invoice_id)`
- `proofpay__release_artifact(invoice_id)`

## Payment rule

A payment is accepted only when a finalized transaction includes the per-invoice reference and an exact configured-mint balance delta for the configured recipient. A reference touch, wrong mint, wrong recipient, underpayment, overpayment, failed transaction, or non-finalized transaction fails closed.

## Quick start

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e '.[dev]'
cp examples/proofpay.toml proofpay.local.toml
# Replace paths and recipient in proofpay.local.toml.
.venv/bin/proofpay-mcp --config proofpay.local.toml
```

Run the test suite:

```bash
.venv/bin/python -m pytest tests -q
```

The stdio integration test launches the actual MCP subprocess, initializes a client session, lists the three tools, and creates an invoice. The production-shaped ZeroClaw receipt is in `docs/zeroclaw-v0.8.4-receipt.json`; the synthetic paid-release receipt is in `docs/demo-receipt.json`.

## ZeroClaw

Install ZeroClaw, then merge `examples/zeroclaw-config-snippet.toml` into its config and grant the `revenue` MCP bundle only to the intended agent. Copy `skills/proofpay/SKILL.md` into that agent's skill bundle.

```bash
zeroclaw --version
zeroclaw --config-dir /path/to/config status
```

ProofPay has been exercised against ZeroClaw v0.8.4's current MCP schema. Absolute paths are intentional: the spawned stdio process must not depend on shell activation.

## Architecture

```text
buyer/channel -> ZeroClaw agent -> narrow MCP tools -> ProofPay policy
                                                    |-> Solana JSON-RPC
                                                    |-> SQLite invoice state
                                                    `-> AES-GCM sealed artifact
```

## Security and scope

Read `docs/THREAT_MODEL.md` before deployment. This prototype handles invoice creation, exact payment verification, and local release. It does not provide buyer authentication, refunds, disputes, tax handling, sanctions screening, or encrypted buyer delivery.

## License

MIT
