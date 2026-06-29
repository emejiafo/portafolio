"""Phase 1 integration test for quote request persistence."""

import asyncio
from uuid import UUID, uuid4

from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database import engine
from app.db.session import engine as async_db_engine
from app.main import app
from app.models.quote_request import QuoteRequest


def _get_quote_by_id(quote_id: UUID):
    with Session(engine) as db:
        result = db.execute(select(QuoteRequest).where(QuoteRequest.id == quote_id))
        return result.scalar_one_or_none()


def _delete_quote_by_id(quote_id: UUID):
    with Session(engine) as db:
        db.execute(delete(QuoteRequest).where(QuoteRequest.id == quote_id))
        db.commit()


def _dispose_async_engine_pool():
    """Dispose pooled asyncpg connections using a dedicated event loop."""
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(async_db_engine.dispose())
    finally:
        loop.close()


async def _submit_quote_request(payload: dict):
    """Submit quote request using one event loop to avoid asyncpg loop mismatch."""
    await async_db_engine.dispose()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/api/public/contact/quote", json=payload)
    await async_db_engine.dispose()
    return response


def test_public_quote_request_persists_to_db():
    _dispose_async_engine_pool()

    payload = {
        "name": "Phase One Prospect",
        "email": f"phase1-{uuid4().hex[:10]}@example.com",
        "company": "Acme Analytics",
        "phone": "+52 55 1111 2222",
        "project_type": "forecasting",
        "budget_range": "50k-100k",
        "timeline": "6 weeks",
        "description": "Need a forecasting model with API delivery and dashboard outputs.",
    }

    response = asyncio.run(_submit_quote_request(payload))

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["status"] == "new"

    quote_id = UUID(response_data["id"])
    persisted = _get_quote_by_id(quote_id)

    try:
        assert persisted is not None
        assert persisted.email == payload["email"]
        assert persisted.description == payload["description"]
        assert persisted.status == "new"
    finally:
        _delete_quote_by_id(quote_id)
