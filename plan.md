# Public Profile and Portfolio Showcase - Transition Plan

## Executive Summary

This plan transitions the project from a solo developer hour tracker into a public profile and portfolio showcase site.

Primary product goals:
- Public profile page with professional summary and a CV link
- CV hosted within the same application and viewable from the profile page
- Public project showcase with filtering and project detail views
- Public contact page that creates quote requests in the database

Transition strategy:
- Non-breaking, phased rollout
- Keep existing infrastructure (Docker Compose, FastAPI, PostgreSQL, Gradio, Nginx)
- Preserve legacy hour-tracker behavior during transition, then deprecate and remove

---

## Product Scope

### In Scope (Target MVP)
- Public-facing portfolio web app
- Profile content from database-backed settings/profile records
- Project catalog from public projects only (`is_public = true`)
- Contact/quote form that writes to `quote_requests`
- CV delivery from local mounted storage and linked from profile page

### Out of Scope (for this transition)
- Authentication and user accounts
- Billing, invoicing, payments, expense workflows
- Rebuilding full admin dashboard UX
- Cloud deployment changes (local Docker remains primary)

---

## Current Codebase Snapshot (June 2026)

### What already exists and is reusable
- Public API modules exist:
  - `backend/app/api/public/portfolio.py`
  - `backend/app/api/public/contact.py`
- Portfolio-related models and tables already exist:
  - `projects`, `technologies`, `project_technologies`, `project_assets`, `profile_info`, `quote_requests`
- Frontend service already runs as a single Gradio app at port 7860.
- Nginx already routes `/` to frontend and `/api` to backend.

### What still reflects hour-tracker mode
- Frontend UI in `frontend/public_app/main.py` is currently an hour tracker.
- API v1 router currently prioritizes clients/projects/time-entries/dashboard.
- Existing plan and docs are still centered on time tracking.

### Critical alignment gaps to address first
- Public router (`backend/app/api/public/router.py`) is currently placeholder/stub and does not include real public modules.
- Some ORM models differ from migration/schema expectations (must be stabilized before feature expansion).
- Public portfolio schema naming/contracts are inconsistent in places and need normalization.

---

## Target User Experience

### Page 1: Profile
- Hero section: name, title, location, short bio
- Skills summary and social links
- CV section:
  - "View CV" link/button
  - Embedded CV preview in page (PDF iframe/object)
  - Optional download action

### Page 2: Projects Showcase
- Public project cards with title, short summary, thumbnail
- Filter by technology and optional project type
- Project detail view with:
  - Full description
  - Tech stack
  - Links (live site, repository)
  - Asset gallery

### Page 3: Contact / Quote
- Contact form fields: name, email, company, phone, project type, budget range, timeline, description
- Submit creates a `quote_requests` record
- User receives success/failure feedback in UI

---

## Architecture Overview (Target)

```
+---------------------------------------------------------------+
|                      Docker Compose Stack                      |
+---------------------------------------------------------------+
|                                                               |
|  +-----------+        +------------------+                    |
|  |  Nginx    |------->|  Gradio Frontend |                    |
|  |  :80      |        |  Portfolio Site  |                    |
|  +-----------+        |  :7860           |                    |
|       |               +------------------+                    |
|       |                        |                               |
|       v                        v                               |
|  +----------------------------------------------------------+  |
|  |                  FastAPI Backend :8000                  |  |
|  |     Public API + Admin API (compat during transition)   |  |
|  +----------------------------------------------------------+  |
|                               |                                |
|                               v                                |
|                  +----------------------------+                |
|                  |      PostgreSQL :5432      |                |
|                  +----------------------------+                |
|                                                               |
+---------------------------------------------------------------+
```

---

## Data Model Focus

### Active tables for portfolio phase
- `profile_info`
  - Stores profile keys such as full name, title, bio, location, social links, CV path/url
- `projects`
  - Source of showcase entries (`is_public`, `display_order`, `slug`, summaries, links)
- `technologies` and `project_technologies`
  - Project filtering and tech stack display
- `project_assets`
  - Thumbnails and media assets for project cards/detail pages
- `quote_requests`
  - Public contact submissions

### Legacy tables to de-emphasize
- `time_entries`, `clients` (hour-tracker context), dashboard hour summaries
- These remain in DB during transition to avoid breaking migrations/history

---

## Public API Contract (Target)

### Portfolio
- `GET /api/public/portfolio/profile`
  - Returns normalized public profile payload including CV metadata
- `GET /api/public/portfolio/projects`
  - Returns public projects, optional `technology` and `project_type` filters
- `GET /api/public/portfolio/projects/{slug}`
  - Returns one public project by slug
- `GET /api/public/portfolio/technologies`
  - Returns available tech filters

### Contact
- `POST /api/public/contact/quote`
  - Creates quote request with validation and default status

### Compatibility
- Keep existing admin endpoints operational during rollout.
- Keep `/api/v1` mounted while frontend cutover is in progress.

---

## CV Hosting and Delivery Strategy

### Storage
- Store CV in mounted local storage under:
  - `data/uploads/assets/cv/`

### Exposure
- Provide a stable URL for current CV (for example a fixed filename path or backend alias endpoint).
- Include CV reference in profile payload (example keys: `cv_url`, `cv_label`, `cv_updated_at`).

### Frontend behavior
- Profile page shows a clear "View CV" action.
- CV is rendered directly in-page using an embedded PDF viewer.
- Optional fallback download link if browser PDF embedding fails.

---

## Non-Breaking Transition Phases

## Phase 0 - Stabilize Contracts (must complete first)

Goals:
- Ensure existing code paths are internally consistent before adding new behavior.

Tasks:
- Wire real public routers in `backend/app/api/public/router.py` instead of placeholders.
- Align model/schema/CRUD naming mismatches that can break portfolio/contact endpoints.
- Add smoke tests for:
  - `GET /api/public/portfolio/profile`
  - `GET /api/public/portfolio/projects`
  - `POST /api/public/contact/quote`

Acceptance criteria:
- Public endpoints return valid responses from database-backed logic.
- No regressions in existing running services.

## Phase 1 - Backend Portfolio Readiness

Goals:
- Make backend fully capable of serving profile/projects/contact requirements.

Tasks:
- Normalize profile payload contract for frontend consumption.
- Ensure projects endpoint includes technology/assets in response as needed.
- Validate quote form payload and persistence path end-to-end.
- Seed minimum public content (profile + at least 2 public projects) for development.

Acceptance criteria:
- Frontend can be implemented without backend workarounds.
- Contact submissions persist and are queryable.

## Phase 2 - Frontend Portfolio Build (parallel-safe)

Goals:
- Implement public portfolio UX while preserving compatibility.

Tasks:
- Replace hour-tracker tabs with three sections/pages:
  - Profile
  - Projects
  - Contact
- Add CV in-page viewer on profile section.
- Add project cards + project detail rendering.
- Add contact form submission + success/error states.

Acceptance criteria:
- Portfolio site is usable at `/`.
- Profile, projects, and contact flow are functional in Docker environment.

## Phase 3 - Cutover and Deprecation

Goals:
- Officially shift product intent away from hour tracking.

Tasks:
- Update documentation (`README.md`) to portfolio-first language.
- Mark hour-tracker endpoints/UI as deprecated.
- Keep legacy API routes available for one transition cycle.

Acceptance criteria:
- All docs and landing UX reflect portfolio product.
- No runtime dependency on hour-tracker frontend modules.

## Phase 4 - Cleanup (post-cutover)

Goals:
- Remove dead code safely once confidence is high.

Tasks:
- Remove hour-tracker frontend logic from `frontend/public_app/main.py`.
- Trim unused API router registrations related only to hour tracker.
- Keep database tables unless migration cleanup is explicitly approved.

Acceptance criteria:
- Codebase is simpler and portfolio-focused.
- Legacy removals do not break compose startup or public endpoints.

## Phase 5 - Controlled Decoupling (post-cleanup hardening)

Goals:
- Reduce runtime coupling between active portfolio models and legacy hour-tracker models.
- Preserve existing legacy tables and migration history.

Tasks:
- Remove active `Project` bi-directional ORM relationships that depend on legacy entities.
- Convert legacy-side project links to one-way relationships where needed.
- Keep DB columns/FKs and Alembic metadata imports intact.
- Add regression checks that remaining active routes still behave correctly.

Acceptance criteria:
- Public portfolio APIs and minimal v1 projects route keep working.
- Removed legacy routes remain unavailable.
- Full test suite remains green.

## Phase 6 - Legacy Data Retirement (schema-level)

Goals:
- Retire legacy hour-tracker tables from the active runtime schema.
- Preserve historical data in explicit archive tables.

Tasks:
- Create migration that snapshots legacy tables to `legacy_archive_*` tables.
- Drop active legacy tables (`clients`, `invoices`, `invoice_items`, `payments`,
  `time_entries`, `expenses`).
- Remove obsolete project schema linkage (`projects.client_id`).
- Remove legacy model files/imports from active runtime metadata registration.

Acceptance criteria:
- Legacy tables no longer exist under active names.
- Archive tables exist with copied historical data.
- Public and minimal v1 APIs remain functional.

---

## Implementation Checklist (Execution Order)

1. Stabilize public router wiring and schema/model consistency.
2. Add/repair tests for public profile/projects/contact endpoints.
3. Define and freeze public response payloads.
4. Build portfolio frontend pages with CV embed.
5. Validate quote request flow from UI to DB.
6. Update docs and deprecate hour-tracker behavior.
7. Remove legacy hour-tracker code in a separate cleanup pass.
8. Decouple active runtime models from legacy relationships while preserving tables.
9. Archive and retire legacy hour-tracker tables from active schema.

---

## Quick Start (Portfolio Mode)

```bash
# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Public portfolio app
http://localhost:7860

# API documentation
http://localhost:8000/docs
```

---

## Risks and Mitigations

- Risk: Hidden schema mismatch causes runtime errors in public endpoints.
  - Mitigation: Contract stabilization first, then feature work.

- Risk: Breaking existing users/scripts relying on hour-tracker routes.
  - Mitigation: Deprecate in phases, preserve compatibility routes during transition.

- Risk: CV file path handling differs by environment.
  - Mitigation: Use deterministic storage path and include integration check in smoke tests.

- Risk: Frontend shift creates temporary UX instability.
  - Mitigation: Keep backend contracts stable and ship frontend in incremental PR-sized steps.

---

## Definition of Done

The transition is complete when:
- The public site is profile/portfolio/contact-first.
- Profile page includes a working in-page CV view and link.
- Projects showcase renders public projects from database data.
- Contact page creates quote requests reliably.
- Hour-tracker behavior is deprecated and removed without breaking deployment.
