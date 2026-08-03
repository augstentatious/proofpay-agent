# Execution plan

## Current verified baseline

- Public repository: https://github.com/augstentatious/proofpay-agent
- ZeroClaw v0.8.4 selected `proofpay__create_invoice` through MCP stdio.
- The invoice row and sealed artifact were written; the plaintext source was removed after commit.
- Eleven tests cover policy locking, exact payment matching, reference-touch skipping, tamper failure, release gating, config, MCP, and process-level stdio.
- A clean wheel install exposed a working `proofpay-mcp` console command.

## Honest gap

The public receipt proves agent-driven invoice creation, not a chain payment. Bounty submission waits for a real channel and an explorer-verifiable devnet or mainnet payment.

## First 72 hours

### 0-12 hours: chain proof

1. Add a devnet smoke harness that keeps payer/operator keys outside ZeroClaw.
2. Use a fresh token mint or devnet USDC and a unique invoice reference.
3. Execute an exact transfer, poll through the MCP status tool, and release the committed artifact.
4. Save transaction signature, explorer URL, returned hashes, and literal command outputs.
5. Add negative live fixtures for wrong amount and reference-only activity if economical.

Exit gate: one explorer-verifiable transfer changes the same invoice from pending to paid and releases byte-identical plaintext.

### 12-24 hours: real channel

1. Configure a dedicated Telegram bot in the isolated ZeroClaw profile.
2. Bind it only to John's Telegram account.
3. Keep `create_invoice` auto-approved; require approval for release and any future refund path.
4. Run the complete conversation from request to invoice to paid confirmation to delivery.
5. Capture a prompt-injection attempt that asks the agent to change recipient, amount, or release early; show policy rejection.

Exit gate: the phone channel shows the full job and the local trace contains the corresponding MCP receipts.

### 24-48 hours: showcase

1. Record one continuous video under three minutes: phone request, QR/URI, wallet payment, confirmation, delivery, terminal receipt.
2. Keep the narration factual: T1, no signing key, operator-owned policy, custom artifact commitment.
3. Add the video URL and live receipt to the repository.
4. Run a clean-room setup from the README on a fresh directory.

### 48-72 hours: submit and respond

1. Post the showcase in ZeroClaw Discord `#solana-bounty`.
2. Submit the same showcase URL on Superteam Earn.
3. Publish one restrained build log on X for the stated tiebreaker.
4. Monitor sponsor questions; answer with receipts or patches, not roadmap claims.

## Thirty-day revenue path

- Week 1: finish and submit the bounty package. Expected payout remains uncertain until judging.
- Week 2: turn ProofPay into a reusable paid-delivery service for custom reports, code reviews, datasets, and model evaluations.
- Week 3: recruit three design partners who already sell digital work; measure invoice completion and setup time.
- Week 4: choose from evidence: maintain the open-source primitive, offer paid setup/support, or build a hosted encrypted-delivery layer.

Do not spend the month on airdrop sybils, flash-loan bots, fake identities, or generalized “agent army” infrastructure. The immediate asset is a tested product plus a live sponsor-defined distribution channel.
