# LWA Worlds Payout State Machine

## Rule

No real payouts in MVP.

The MVP tracks estimated, pending, and approved earnings only.

## States

1. `not_eligible`
2. `estimated`
3. `pending_review`
4. `approved`
5. `payable`
6. `processing`
7. `paid`
8. `failed`
9. `held`
10. `disputed`
11. `refunded`
12. `cancelled`

## Allowed Transitions

- estimated -> pending_review
- pending_review -> approved
- pending_review -> held
- pending_review -> disputed
- approved -> payable
- approved -> held
- payable -> processing
- processing -> paid
- processing -> failed
- held -> approved
- held -> cancelled
- disputed -> approved
- disputed -> refunded
- disputed -> cancelled

## Forbidden Transitions

- estimated -> paid
- pending_review -> paid
- disputed -> paid
- refunded -> paid
- cancelled -> paid
- held -> paid without review
- any state -> paid without audit log

## Required Data

- earning owner
- source campaign
- source submission
- amount
- platform fee
- current status
- review status
- dispute status
- payout eligibility
- audit logs

## Stripe Connect Future Mapping

- approved/payable maps to connected account payout eligibility.
- processing maps to transfer/payout processing.
- paid maps to completed payout confirmation.
- failed maps to Stripe failure event.
- held/disputed maps to admin/platform hold.

## Safety Copy

Earnings are not guaranteed. Payouts require review and approval. Payouts may be held during disputes, fraud checks, refunds, or content rights review.
