# LWA Worlds Status Transitions

## Campaign

Allowed:

- draft -> pending_review
- pending_review -> open
- pending_review -> rejected
- open -> in_progress
- open -> cancelled
- in_progress -> submitted
- submitted -> under_review
- under_review -> revision_requested
- under_review -> completed
- under_review -> disputed
- disputed -> completed
- disputed -> cancelled

Forbidden:

- draft -> completed
- pending_review -> completed
- open -> paid
- cancelled -> open without admin
- disputed -> paid without resolution

## Submission

Allowed:

- draft -> submitted
- submitted -> under_review
- under_review -> approved
- under_review -> rejected
- under_review -> revision_requested
- revision_requested -> submitted
- approved -> paid
- approved -> disputed
- disputed -> approved
- disputed -> rejected
- paid -> disputed only with admin review

Forbidden:

- submitted -> paid
- rejected -> paid
- revision_requested -> paid
- disputed -> paid without admin resolution

## Earnings

Allowed:

- estimated -> pending_review
- pending_review -> approved
- pending_review -> held
- approved -> payable
- payable -> processing
- processing -> paid
- processing -> failed
- held -> approved
- held -> cancelled
- disputed -> refunded
- disputed -> approved

Forbidden:

- estimated -> paid
- pending_review -> paid
- held -> paid
- disputed -> paid
- refunded -> paid
