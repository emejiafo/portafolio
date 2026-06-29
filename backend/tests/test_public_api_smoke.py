"""Phase 0 smoke tests for public portfolio endpoints."""

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.api.public import contact as contact_api
from app.api.public import portfolio as portfolio_api
from app.main import app


class _ScalarResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _ExecuteResult:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self):
        return _ScalarResult(self._rows)


class _FakeSession:
    def __init__(self, profile_rows):
        self._profile_rows = profile_rows

    async def execute(self, _statement):
        return _ExecuteResult(self._profile_rows)


@pytest.fixture
def client():
    profile_rows = [
        SimpleNamespace(
            key="full_name",
            value="Jane Doe",
            value_type="text",
            category="personal",
        ),
        SimpleNamespace(
            key="professional_title",
            value="Machine Learning Engineer",
            value_type="text",
            category="professional",
        ),
    ]

    async def override_get_db():
        yield _FakeSession(profile_rows)

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_public_profile_smoke(client):
    response = client.get("/api/public/portfolio/profile")

    assert response.status_code == 200
    payload = response.json()
    assert payload["full_name"] == "Jane Doe"
    assert payload["professional_title"] == "Machine Learning Engineer"
    assert isinstance(payload["skills"], list)


def test_public_projects_smoke(client, monkeypatch):
    async def fake_get_public(_db, *, skip=0, limit=100):
        return [
            SimpleNamespace(
                id=uuid4(),
                title="Churn Prediction",
                slug="churn-prediction",
                short_description="Predict customer churn from behavior logs.",
                full_description="End-to-end modeling and deployment.",
                project_type="ml",
                start_date=None,
                end_date=None,
                github_url="https://github.com/example/churn",
                live_url=None,
                thumbnail_path=None,
                display_order=1,
                technologies=[
                    SimpleNamespace(
                        id=uuid4(),
                        name="Python",
                        category="language",
                        icon_url=None,
                        color="#3776AB",
                    )
                ],
                assets=[
                    SimpleNamespace(
                        id=uuid4(),
                        asset_type="image",
                        file_path="/uploads/assets/projects/churn-dashboard.png",
                        original_filename="churn-dashboard.png",
                        mime_type="image/png",
                        file_size=None,
                        sort_order=0,
                        created_at=datetime.now(timezone.utc),
                    )
                ],
            )
        ]

    monkeypatch.setattr(portfolio_api.project_crud, "get_public", fake_get_public)

    response = client.get("/api/public/portfolio/projects")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) == 1
    assert payload[0]["slug"] == "churn-prediction"
    assert payload[0]["technologies"][0]["name"] == "Python"
    assert payload[0]["assets"][0]["asset_type"] == "image"


def test_public_quote_submission_smoke(client, monkeypatch):
    async def fake_create(_db, *, obj_in):
        now = datetime.now(timezone.utc)
        data = obj_in.model_dump()
        return SimpleNamespace(
            id=uuid4(),
            status="new",
            notes=None,
            converted_project_id=None,
            created_at=now,
            updated_at=now,
            **data,
        )

    monkeypatch.setattr(contact_api.quote_crud, "create", fake_create)

    response = client.post(
        "/api/public/contact/quote",
        json={
            "name": "Acme Corp",
            "email": "contact@acme.com",
            "company": "Acme",
            "phone": "+52-55-0000-0000",
            "project_type": "ml_model",
            "budget_range": "50k-100k",
            "timeline": "6 weeks",
            "description": "Need a demand forecasting model.",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "new"
    assert payload["email"] == "contact@acme.com"


def test_public_quote_validation_rejects_short_description(client):
    response = client.post(
        "/api/public/contact/quote",
        json={
            "name": "Lead",
            "email": "lead@example.com",
            "description": "too short",
        },
    )

    assert response.status_code == 422
