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