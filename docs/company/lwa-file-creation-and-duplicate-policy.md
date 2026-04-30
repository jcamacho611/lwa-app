# LWA File Creation And Duplicate Prevention Policy

## Purpose

This policy controls how new files are created in the LWA repo so future ChatGPT, Codex, Claude, and human work does not create unnecessary duplicates or overwrite good work.

## Default rule

Before creating any file:

1. Search the repo for the intended topic.
2. Fetch the exact target path if it might exist.
3. If the file exists, update it.
4. If the file does not exist, create it.
5. Do not create duplicate files unnecessarily.

## Allowed automatic creation

It is acceptable to create a new file when:

- the target path does not already exist
- the file has a clearly different purpose from existing docs/code
- the file belongs in the correct folder
- the file does not replace working implementation
- the file does not touch `lwa-ios` unless explicitly requested
- the file does not add live payouts, blockchain contracts, direct social posting, or marketplace money movement without a dedicated approved task

## Update instead of create

Update an existing file when:

- it covers the same topic
- it is the established source of truth
- it is already linked from an index
- the new content is an expansion or correction
- creating another file would split the same audience/workflow

## Keep both files only when purpose differs

Two similar files can both remain if they serve different audiences.

Examples:

- `docs/company/*` = source-of-truth, status, claim safety, architecture compatibility, repo operating system
- `docs/lwa-worlds/*` = execution artifacts, prompts, sales/ops/hiring docs, algorithm docs
- `docs/lwa-worlds/sql/*` = SQL/migration blueprint, not live production migration

## Delete only after audit

Delete or consolidate a file only when:

1. it is clearly duplicative,
2. a stronger/current version exists,
3. it is not referenced by README/index/docs,
4. it is not used by tests/code/imports,
5. deleting it will not remove unique business, product, or engineering content.

When unsure, keep the file and add a note explaining its purpose.

## Branch rule

If a branch has zero commits ahead of `main`, do not open or merge a PR from it.

If a branch is diverged, check whether its file changes already exist on `main` before reopening/merging.

Do not re-merge stale branches just to make activity.

## Commit rule

Commit only isolated, reviewable changes.

Good commit examples:

- `docs: add LWA file creation policy`
- `docs: update LWA artifact index`
- `backend: add Whop webhook verification`
- `web: display Director Brain package fields`

Avoid commits that mix unrelated code, docs, payments, blockchain, and frontend redesign in one change.

## Safety rule

Never create files that imply unfinished systems are live.

Do not claim:

- guaranteed virality
- guaranteed income
- verified payment without webhook verification
- live marketplace payouts without ledger/KYC/dispute system
- live direct social posting without provider approval
- live blockchain/NFT product without legal/product approval

## Operating instruction for future AI work

Use this exact rule before creating files:

```text
Search/fetch the target file first. If it exists, update it. If it does not exist, create it. Do not create duplicate docs or code. If similar files exist, explain why the new file is necessary before creating it.
```
