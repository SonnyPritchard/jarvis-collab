"""
Minimal FastAPI federation router (v1.1-ish)
- Capabilities
- Negotiate
- Result
- Progress
- Progress timeline read
Includes:
- API key check
- HMAC signature check
- timestamp + nonce replay guard
- idempotency key handling

Env vars expected:
- FEDERATION_API_KEY
- FEDERATION_HMAC_SECRET
- INSTANCE_ID (default: jarvis-instance)
- INSTANCE_NAME (default: Jarvis)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, List

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/federation", tags=["federation"])

FEDERATION_API_KEY = os.getenv("FEDERATION_API_KEY", "")
FEDERATION_HMAC_SECRET = os.getenv("FEDERATION_HMAC_SECRET", "")
INSTANCE_ID = os.getenv("INSTANCE_ID", "jarvis-instance")
INSTANCE_NAME = os.getenv("INSTANCE_NAME", "Jarvis")

# In-memory stores for MVP; replace with Redis in production.
_seen_nonces: Dict[str, float] = {}
_idempotency_cache: Dict[str, Dict[str, Any]] = {}
_progress_store: Dict[str, List[Dict[str, Any]]] = {}


def _prune_nonces(now: float, ttl: int = 300) -> None:
    dead = [k for k, ts in _seen_nonces.items() if now - ts > ttl]
    for k in dead:
        _seen_nonces.pop(k, None)


def _verify_headers(
    body: bytes,
    x_api_key: str,
    x_timestamp: str,
    x_nonce: str,
    x_signature: str,
) -> None:
    if not FEDERATION_API_KEY or not FEDERATION_HMAC_SECRET:
        raise HTTPException(status_code=500, detail="Federation secrets not configured")

    if x_api_key != FEDERATION_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    now = int(time.time())
    try:
        ts = int(x_timestamp)
    except ValueError:
        raise HTTPException(status_code=400, detail="Bad timestamp")

    if abs(now - ts) > 60:
        raise HTTPException(status_code=401, detail="Stale timestamp")

    _prune_nonces(now)
    if x_nonce in _seen_nonces:
        raise HTTPException(status_code=409, detail="Nonce replay detected")

    canonical = f"{x_timestamp}.{x_nonce}.".encode("utf-8") + body
    expected = hmac.new(
        FEDERATION_HMAC_SECRET.encode("utf-8"),
        canonical,
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, x_signature):
        raise HTTPException(status_code=401, detail="Bad signature")

    _seen_nonces[x_nonce] = now


class FederationEnvelope(BaseModel):
    protocol_version: str = "1.1"
    task_id: str
    from_instance: str | None = None
    to_instance: str | None = None
    intent: str
    payload: Dict[str, Any] = Field(default_factory=dict)


@router.get("/capabilities")
def get_capabilities() -> Dict[str, Any]:
    return {
        "instance_id": INSTANCE_ID,
        "instance_name": INSTANCE_NAME,
        "protocol_version": "1.1",
        "agents": [
            {"id": "scheme-scout", "role": "research", "strengths": ["research", "discovery"]},
            {"id": "scheme-scorer", "role": "evaluator", "strengths": ["scoring", "ranking"]},
            {"id": "scheme-killer", "role": "redteam", "strengths": ["risk", "falsification"]},
            {"id": "experiment-designer", "role": "builder", "strengths": ["experiments", "validation"]},
            {"id": "ops-monitor", "role": "ops", "strengths": ["monitoring", "incident triage"]},
            {"id": "memory-curator", "role": "memory", "strengths": ["distillation", "continuity"]},
        ],
        "subtask_taxonomy": [
            "research",
            "scoring",
            "redteam",
            "experiment_design",
            "implementation",
            "test",
            "review",
            "synthesis",
        ],
        "endpoints": {
            "negotiate": "/federation/negotiate",
            "result": "/federation/result",
            "progress": "/federation/progress",
            "timeline": "/federation/progress/{task_id}",
        },
    }


@router.post("/negotiate")
async def negotiate(
    request: Request,
    envelope: FederationEnvelope,
    x_api_key: str = Header("", alias="X-API-Key"),
    x_timestamp: str = Header("", alias="X-Timestamp"),
    x_nonce: str = Header("", alias="X-Nonce"),
    x_signature: str = Header("", alias="X-Signature"),
    x_idempotency_key: str = Header("", alias="X-Idempotency-Key"),
) -> Dict[str, Any]:
    raw = await request.body()
    _verify_headers(raw, x_api_key, x_timestamp, x_nonce, x_signature)

    if x_idempotency_key and x_idempotency_key in _idempotency_cache:
        return _idempotency_cache[x_idempotency_key]

    needed = envelope.payload.get("subtasks_needed", [])
    local_strengths = {
        "research": "scheme-scout",
        "scoring": "scheme-scorer",
        "redteam": "scheme-killer",
        "experiment_design": "experiment-designer",
        "review": "scheme-killer",
        "synthesis": "memory-curator",
    }
    claimed = [s for s in needed if s in local_strengths]

    resp = {
        "task_id": envelope.task_id,
        "responder": INSTANCE_ID,
        "can_contribute": len(claimed) > 0,
        "claimed_subtasks": claimed,
        "assigned_agents": {s: local_strengths[s] for s in claimed},
        "cannot_do": [s for s in needed if s not in local_strengths],
        "status": "ok",
    }

    if x_idempotency_key:
        _idempotency_cache[x_idempotency_key] = resp
    return resp


@router.post("/result")
async def result(
    request: Request,
    envelope: FederationEnvelope,
    x_api_key: str = Header("", alias="X-API-Key"),
    x_timestamp: str = Header("", alias="X-Timestamp"),
    x_nonce: str = Header("", alias="X-Nonce"),
    x_signature: str = Header("", alias="X-Signature"),
    x_idempotency_key: str = Header("", alias="X-Idempotency-Key"),
) -> Dict[str, Any]:
    raw = await request.body()
    _verify_headers(raw, x_api_key, x_timestamp, x_nonce, x_signature)

    if x_idempotency_key and x_idempotency_key in _idempotency_cache:
        return _idempotency_cache[x_idempotency_key]

    rec = {
        "event": "result",
        "task_id": envelope.task_id,
        "payload": envelope.payload,
        "received_at": int(time.time()),
    }
    _progress_store.setdefault(envelope.task_id, []).append(rec)

    resp = {"status": "ok", "task_id": envelope.task_id, "stored": True}
    if x_idempotency_key:
        _idempotency_cache[x_idempotency_key] = resp
    return resp


@router.post("/progress")
async def progress(
    request: Request,
    envelope: FederationEnvelope,
    x_api_key: str = Header("", alias="X-API-Key"),
    x_timestamp: str = Header("", alias="X-Timestamp"),
    x_nonce: str = Header("", alias="X-Nonce"),
    x_signature: str = Header("", alias="X-Signature"),
    x_idempotency_key: str = Header("", alias="X-Idempotency-Key"),
) -> Dict[str, Any]:
    raw = await request.body()
    _verify_headers(raw, x_api_key, x_timestamp, x_nonce, x_signature)

    if x_idempotency_key and x_idempotency_key in _idempotency_cache:
        return _idempotency_cache[x_idempotency_key]

    item = {
        "event": envelope.payload.get("event", "progress"),
        "task_id": envelope.task_id,
        "payload": envelope.payload,
        "received_at": int(time.time()),
    }
    _progress_store.setdefault(envelope.task_id, []).append(item)

    resp = {"status": "ok", "task_id": envelope.task_id, "accepted": True}
    if x_idempotency_key:
        _idempotency_cache[x_idempotency_key] = resp
    return resp


@router.get("/progress/{task_id}")
def progress_timeline(task_id: str) -> Dict[str, Any]:
    return {
        "task_id": task_id,
        "events": _progress_store.get(task_id, []),
        "count": len(_progress_store.get(task_id, [])),
    }


def build_signature(secret: str, timestamp: int, nonce: str, body_obj: Dict[str, Any]) -> str:
    """Helper for clients/tests."""
    body = json.dumps(body_obj, separators=(",", ":")).encode("utf-8")
    canonical = f"{timestamp}.{nonce}.".encode("utf-8") + body
    return hmac.new(secret.encode("utf-8"), canonical, hashlib.sha256).hexdigest()
