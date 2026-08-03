---
name: proofpay
description: Create payment-gated invoices and release sealed deliverables.
version: "0.1.0"
author: augstentatious
license: MIT
category: tools
tags:
  - Community
  - Solana
  - Payments
permissions: []
---

# ProofPay

Use ProofPay only for an artifact already present in the operator-owned artifact root.

## Flow

1. Call `proofpay__create_invoice` with `artifact_name`, decimal `amount`, and an optional buyer label.
2. Return the generated Solana Pay URI and invoice ID to the buyer.
3. Call `proofpay__invoice_status` to poll finalized chain state.
4. Call `proofpay__release_artifact` only after status is `paid`.
5. Return the released file path to the operator/channel delivery layer.

## Boundaries

- Recipient, mint, amount ceiling, roots, RPC, and decimals are operator config, not model arguments.
- Never request, expose, log, or transmit wallet private keys.
- Never claim payment before `invoice_status` returns `paid`.
- A failed integrity check is terminal for that artifact until an operator restores it.
- Do not release plaintext for `pending` or `expired` invoices.
