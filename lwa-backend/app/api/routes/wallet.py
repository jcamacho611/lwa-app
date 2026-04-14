from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from ...dependencies.auth import get_platform_store, require_user
from ...models.schemas import PayoutRequestCreate

router = APIRouter(prefix="/v1/wallet", tags=["wallet"])
platform_store = get_platform_store()
logger = logging.getLogger("uvicorn.error")


@router.get("")
async def wallet_summary(request: Request) -> dict[str, object]:
    user = require_user(request)
    wallet = platform_store.get_wallet(user_id=user.id)
    submission_summary = platform_store.get_user_submission_summary(user_id=user.id)
    credits = [entry["amount_cents"] for entry in wallet["transactions"] if entry["amount_cents"] > 0]
    debits = [abs(entry["amount_cents"]) for entry in wallet["transactions"] if entry["amount_cents"] < 0]
    pending = sum(payout["amount_cents"] for payout in wallet["payouts"] if payout["status"] == "pending")
    return {
        "pending_cents": pending,
        "available_cents": max(wallet["balance_cents"], 0),
        "lifetime_cents": sum(credits),
        "currency": "USD",
        "recent_entries": wallet["transactions"][:10],
        "pending_debits_cents": sum(debits),
        "eligible_payout_cents": submission_summary["eligible_payout_cents"],
        "submission_summary": submission_summary,
    }


@router.get("/ledger")
async def wallet_ledger(request: Request) -> dict[str, object]:
    user = require_user(request)
    return {"entries": platform_store.list_ledger_entries(user_id=user.id)}


@router.post("/payout-requests")
async def create_payout_request(payload: PayoutRequestCreate, request: Request) -> dict[str, object]:
    user = require_user(request)
    try:
        payout = platform_store.request_payout(user_id=user.id, amount_cents=payload.amount_cents)
        logger.info("payout_request_created user_id=%s payout_id=%s amount_cents=%s", user.id, payout["id"], payload.amount_cents)
        return payout
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
