# Off-Chain Proof Scaffold

## Status

This is an off-chain provenance scaffold. It is not a token launch, chain deployment, wallet feature, or investment product.

## Current files

- `lwa-backend/app/services/proof_core.py`
- `lwa-backend/tests/test_proof_core.py`

## Current primitives

- deterministic proof records
- canonical JSON hashing
- proof leaves
- deterministic Merkle root helper
- daily proof snapshot helper
- provenance-only disclosure helper

## Rules

- Proof records are provenance only.
- No investment language.
- No yield or payout language.
- No tokenomics.
- No app feature unlocks.
- No blockchain deployment in this phase.

## Future order

1. Store proof records durably.
2. Emit daily snapshots.
3. Add proof lookup routes.
4. Add frontend proof display.
5. Evaluate optional chain anchoring later in a separate phase.

## Claim boundary

Do not describe badges, relics, or proof records as financial assets. Do not describe this scaffold as deployed on-chain.
