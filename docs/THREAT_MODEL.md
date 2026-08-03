# Threat model

## Protected assets

- plaintext deliverables before settlement
- per-invoice AES-256-GCM keys
- invoice state and payment evidence
- operator policy: recipient, mint, amount ceiling, and file roots

## Trust boundaries

The ZeroClaw model sees three narrow MCP tools. It does not receive encryption keys and cannot set recipient, mint, RPC, decimals, amount ceiling, or storage roots. The local ProofPay process owns those controls.

## Payment acceptance

A payment is accepted only when one finalized Solana transaction contains:

1. the invoice reference account key;
2. the configured recipient token account owner;
3. the configured SPL mint; and
4. an exact positive token-balance delta equal to the invoice base-unit amount.

A transaction that merely touches the reference is skipped. Confirmation below `finalized`, wrong mint, wrong recipient, underpayment, and overpayment all fail closed.

## Artifact protection

Each invoice uses a random 256-bit key and 96-bit nonce. AES-GCM additional authenticated data binds the ciphertext to the invoice ID. The source artifact is deleted only after the sealed file and state row are written. Tampering fails closed before plaintext is written.

## Residual risks

- Host compromise can expose the SQLite key column and released plaintext.
- Public Solana RPC providers observe queries; self-hosted RPC reduces that disclosure.
- The release directory is a local handoff, not an end-to-end buyer transport.
- Blockchain finality and RPC correctness remain external dependencies.
- No refund, dispute, tax, sanctions, or buyer-authentication policy is implemented.

## Operational controls

Run under a dedicated OS user, set state/sealed directories to mode 0700, back up the database and ciphertext together, use a trusted RPC endpoint, and delete released plaintext after channel delivery succeeds.
