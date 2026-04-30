# LWA Worlds Artifact Index

This folder contains the internal artifact system for building, selling, launching, and scaling LWA / IWA.

## Core artifacts

- [Master Build Bible](./master-build-bible.md)
- [Codex Prompt Pack](./codex-prompt-pack.md)
- [Director Brain Algorithm Artifact](./director-brain-algorithm-artifact.md)
- [Master Algorithm + Database Stack](./master-algorithm-database-stack.md)

## Execution artifacts

- [Frontend Rebuild Artifact](./frontend-rebuild-artifact.md)
- [Operations Playbook](./operations-playbook.md)
- [Investor and Sales Artifact](./investor-sales-artifact.md)
- [Founding Council Hiring Artifact](./founding-council-hiring-artifact.md)

## Launch and verification

- [Railway Smoke Test Runbook](../company/lwa-railway-smoke-test-runbook.md)

## Usage rule

Use the Master Build Bible as the source of truth.

Use child artifacts for execution by lane:

- Codex/engineering: Codex Prompt Pack, Director Brain Algorithm Artifact, and Master Algorithm + Database Stack
- Frontend/design: Frontend Rebuild Artifact
- Maria/ops: Operations Playbook
- Sales/investors: Investor and Sales Artifact
- Recruiting: Founding Council Hiring Artifact
- Launch: Railway Smoke Test Runbook

Do not paste the entire Master Build Bible into Codex as one task. Give Codex one narrow prompt at a time.

Do not claim future systems are live until repo evidence, deployment, and smoke tests prove they are live.
