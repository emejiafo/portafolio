"""Tests for Phase 4 cleanup behavior."""

from fastapi.testclient import TestClient

from app.main import app


def test_removed_legacy_v1_routes_return_404():
    removed_paths = [
        "/api/v1/dashboard/summary",
        "/api/v1/time-entries",
        "/api/v1/clients",
        "/api/v1/invoices",
        "/api/v1/payments",
        "/api/v1/expenses",
        "/api/v1/quotes",
        "/api/v1/settings",
        "/api/v1/technologies",
    ]

    with TestClient(app) as client:
        for path in removed_paths:
            response = client.get(path)
            assert response.status_code == 404


def test_legacy_api_alias_removed():
    with TestClient(app) as client:
        response = client.get("/api/projects")

    assert response.status_code == 404


def test_public_api_routes_still_available():
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json().get("paths", {})
    assert "/api/public/portfolio/projects" in paths


def test_minimal_v1_projects_route_still_available():
    with TestClient(app) as client:
        response = client.get("/api/v1/projects/")

    assert response.status_code == 200
