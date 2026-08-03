# Three-minute demo script

## 0:00-0:20 — job

Phone: ask the dedicated ZeroClaw bot to sell `analysis.md` for 0.10 test USDC.

Narration: “This is a custom work product, not a static storefront item. ProofPay commits to the file before asking for payment.”

## 0:20-0:50 — invoice

Show the returned Solana Pay URI or QR and the invoice ID. On the terminal, show the ciphertext path and both hashes. Show that the plaintext source is gone.

## 0:50-1:10 — fail closed

Before payment, ask for release. Show `invoice is not paid`.

Send a malicious buyer message asking the agent to change the recipient and mark the invoice paid. Show that recipient is absent from the tool schema and release remains blocked.

## 1:10-1:45 — real payment

Scan/pay from the separate wallet. Show the explorer transaction and unique reference. The payer key never enters ZeroClaw.

## 1:45-2:15 — verification and delivery

Ask the bot for status. Show `paid`, the finalized signature, and the release result. Open the delivered artifact and show its hash matches the pre-invoice plaintext commitment.

## 2:15-2:40 — boundaries

Show the three-tool MCP schema and operator TOML. State: T1, no signing key, exact recipient/mint/amount/reference/finality checks, supervised release.

## 2:40-3:00 — reproduce

Show the public repository, `pytest` result, ZeroClaw receipt, and setup snippet. End on the explorer URL and repository URL. No slides.
