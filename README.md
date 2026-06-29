# Public Profile And Portfolio Showcase

A portfolio-first platform for a freelance ML engineer, featuring:
- Public profile page with embedded CV support
- Public project showcase with technologies and asset gallery
- Public contact form that creates quote requests
- FastAPI + PostgreSQL backend with Docker Compose local stack

## Quick Start

1. Start all services:
   ```bash
   docker-compose up -d
   ```

2. Run database migrations:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

3. Seed development portfolio data:
   ```bash
   docker-compose exec backend python scripts/seed_data.py
   ```

4. Access the app and APIs:
   - Public Portfolio UI: http://localhost:7860
   - API Documentation: http://localhost:8000/docs
   - Public API Base: http://localhost:8000/api/public
   - Health Check: http://localhost:8000/health

## Public API Endpoints

### Portfolio
- GET `/api/public/portfolio/profile`
- GET `/api/public/portfolio/projects`
- GET `/api/public/portfolio/projects/{slug}`
- GET `/api/public/portfolio/technologies`

### Contact
- POST `/api/public/contact/quote`

## Phase 4 Cleanup Notes

Hour-tracker routes have been removed from active API registration.

Removed endpoints:
- `/api/v1/dashboard/*`
- `/api/v1/time-entries/*`
- `/api/v1/clients/*`
- `/api/v1/invoices/*`
- `/api/v1/payments/*`
- `/api/v1/expenses/*`
- `/api/v1/quotes/*`
- `/api/v1/settings/*`
- `/api/v1/technologies/*`
- Legacy alias `/api/*`

Remaining v1 route set is minimal and non-hour-tracker focused.

## Phase 5 Controlled Decoupling Notes

Legacy tables are preserved, but active portfolio runtime models are no longer
bi-directionally coupled to legacy hour-tracker entities.

What changed:
- `Project` ORM now keeps only portfolio-facing relationships (technologies, assets).
- Legacy ORM links from invoices/time entries/expenses to projects are kept as
   one-way relationships without `back_populates` coupling.
- API project queries no longer eager-load client relationship data.

What stayed intact:
- Existing legacy tables remained in the database at the end of Phase 5.
- Alembic metadata/model imports still include legacy models to preserve migration
   history and table awareness.

## Phase 6 Legacy Retirement Notes

Legacy hour-tracker tables are now retired from the active schema.

What changed:
- Added Alembic migration `002_phase6_legacy_retirement`.
- Copied legacy data into archive tables named `legacy_archive_*`.
- Dropped active legacy tables:
   - `clients`
   - `invoices`
   - `invoice_items`
   - `payments`
   - `time_entries`
   - `expenses`
- Removed `projects.client_id` from the active schema.

Operational notes:
- Migration is intentionally irreversible through Alembic downgrade.
- Archived data remains queryable in `legacy_archive_*` tables for audit/export.

## Development

### View logs
```bash
docker-compose logs -f
```

### Access database
```bash
docker-compose exec db psql -U freelance -d freelance_db
```

### Run tests
```bash
docker-compose exec backend pytest
```

### Run public transition tests only
```bash
docker-compose exec backend pytest tests/test_public_api_smoke.py tests/test_public_quote_e2e.py -q
```

## Project Plan

See [plan.md](plan.md) for transition phases and implementation details.

## License

Private - All rights reserved