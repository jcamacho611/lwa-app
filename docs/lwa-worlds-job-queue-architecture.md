# LWA Worlds Job Queue Architecture

## Purpose

Jobs control long-running work:

- upload processing
- transcript generation
- AI clip scoring
- clip generation
- render generation
- caption generation
- UGC moderation scan
- campaign pack generation
- social import
- trend import

## Job States

- queued
- running
- waiting
- succeeded
- failed
- cancelled
- retrying
- expired

## Required Job Data

- public ID
- owner user ID
- job type
- status
- priority
- progress
- source reference
- target reference
- input JSON
- output JSON
- error message
- attempt count
- timestamps

## Event Logs

Each job should have append-only events for:

- created
- started
- progress update
- retry scheduled
- failed
- succeeded
- cancelled

## Worker Strategy

MVP:

- scaffold job records
- manual/dev run-once endpoint
- no real queue yet

Next:

- Railway worker service
- Redis queue
- Celery/RQ/Dramatiq
- isolated render worker
- retry scheduler

## Safety

Jobs must not:

- charge credits twice
- approve payouts
- skip rights review
- publish without approval
- overwrite outputs silently
- retry destructive operations without idempotency
