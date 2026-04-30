# LWA Worlds Job Retry Policy

## Retryable Jobs

- upload processing
- transcript generation
- AI clip scoring
- clip generation
- render generation
- social import
- trend import

## Non-Retryable Without Review

- payout actions
- entitlement changes
- manual admin decisions
- rights claim resolution
- fraud confirmations

## Default Attempts

- render generation: 3
- clip generation: 3
- transcript generation: 3
- social import: 2
- trend import: 2
- moderation scan: 2
- AI scoring: 2

## Backoff

- attempt 1: 1 minute
- attempt 2: 2 minutes
- attempt 3: 4 minutes
- capped at 30 minutes

## Failure Rules

A job should fail if:

- max attempts reached
- input missing
- source unavailable
- rights check fails
- provider unavailable after retries
- unsafe content blocks processing

## Idempotency

Retrying must not:

- duplicate credits charged
- duplicate earnings created
- duplicate submissions created
- duplicate public posts
- duplicate payout requests
