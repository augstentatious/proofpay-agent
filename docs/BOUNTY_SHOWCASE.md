# Bounty showcase

## Claim

ProofPay gives a ZeroClaw agent a narrow paid-delivery primitive without giving the model wallet keys or mutable payment policy.

## Live path exercised

`ZeroClaw v0.8.4 CLI -> seller agent -> proofpay__create_invoice -> MCP stdio -> AES-GCM seal -> SQLite commitment`

The exact invocation receipt is `docs/zeroclaw-v0.8.4-receipt.json`. It uses the System Program address as a non-spendable demo recipient and claims no mainnet payment.

## Security result

- invoice creation is the only auto-approved ProofPay action in the showcase profile;
- status and release remain supervised;
- plaintext is removed only after ciphertext and invoice state commit;
- exact finalized mint/recipient/amount/reference matching gates release;
- ciphertext tampering raises a controlled error and writes no plaintext;
- a reference-only transaction is skipped while scanning later signatures.

## Reproduction

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest tests -q
```

Then follow `README.md` and merge `examples/zeroclaw-config-snippet.toml` into an isolated ZeroClaw config.

## Demonstration sequence

1. Place a deliverable under the configured artifact root.
2. Ask the ZeroClaw agent to create an invoice.
3. Show the returned URI and ciphertext commitment.
4. Show that release is rejected while pending.
5. In the local fixture demo, supply exact finalized evidence and show release succeeds.
6. Tamper with a ciphertext copy and show release fails closed.

A live-mainnet version of steps 4-5 requires an operator wallet and real USDC; the repository does not fabricate that evidence.
