# Live Solana smoke test

This optional harness creates a real SPL mint on Solana devnet, creates a ProofPay invoice, sends an exact referenced token payment, polls finalized JSON-RPC evidence, and releases the artifact.

No payer secret enters ZeroClaw, MCP arguments, ProofPay config, receipts, or Git.

## Install

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev,devnet]'
```

## Create an operator-only devnet payer

```bash
.venv/bin/python scripts/create_devnet_keypair.py --out /secure/path/devnet-payer.json
```

The helper writes Solana CLI-format bytes with mode `0600`. Fund only the printed public address using a documented Solana devnet faucet.

## Run

```bash
.venv/bin/python scripts/devnet_smoke.py \
  --payer-keypair /secure/path/devnet-payer.json \
  --workdir .devnet-runtime \
  --receipt docs/devnet-receipt.json
```

A successful receipt contains the public mint, recipient, reference, finalized transaction signature, explorer URL, released SHA-256, and `payer_key_in_zeroclaw: false`. It never contains secret bytes.

## Current execution note

On 2026-08-03 the official devnet and testnet `requestAirdrop` methods returned `InternalError` from this host. `devnet-pow` v0.1.4 was also compiled, but its zero-balance bootstrap calls the same airdrop endpoint for the first 5,000 lamports. The community faucet then required interactive GitHub authentication. No live receipt is committed until the chain transaction succeeds.
