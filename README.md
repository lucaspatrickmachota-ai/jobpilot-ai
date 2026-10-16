# JobPilot AI

An explainable job-search workspace for tracking applications, extracting CV text, analysing job descriptions and comparing role requirements with evidence from a CV.

> **Status: MVP under active development.** Code is being published incrementally. CI and container deployment must pass before treating this project as production-ready.

## Features in the current codebase

- Account registration, login and bearer-token authentication.
- Per-user application CRUD and dashboard metrics backed by PostgreSQL.
- PDF CV upload with size, MIME, file-signature and parsing validation.
- Local keyword-based job requirement extraction, explicitly labelled as a baseline.
- Deterministic CV/job matching with a transparent score breakdown, matched skills and missing skills.
- Optional OpenAI-compatible provider adapter for completions, structured extraction and embeddings.
- PostgreSQL/pgvector CV chunks and evidence retrieval when a provider is configured.
- Responsive web UI for account workflows, application management, CV upload and analysis.
- Docker Compose, Alembic migrations, pytest, Vitest, Playwright and GitHub Actions CI configuration.

AI provider features are disabled by default (`AI_PROVIDER=none`). Configure credentials and model names to enable embedding/RAG. No fake application records or fabricated dashboard statistics are seeded.

## Stack

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS
- **Backend:** Python 3.12, FastAPI, Pydantic Settings, SQLAlchemy 2, Alembic
- **Data:** PostgreSQL 16 and pgvector
- **Quality:** pytest, Vitest, Testing Library, ESLint, TypeScript, Ruff, Playwright
- **Local infrastructure:** Docker Compose

## Matching algorithm

Default weights:

| Dimension | Weight |
|---|---:|
| Skills | 50% |
| Experience text signals | 30% |
| Education text signals | 10% |
| Language text signals | 10% |

The final score is a weighted sum of four integer component scores, rounded and clamped to 0–100. Skills use an explicit alias taxonomy and word boundaries. Other dimensions currently use simple textual signals, not semantic judgement. This is a decision-support signal, not a hiring prediction.

## Run locally

Requirements: Docker Engine/Desktop with Docker Compose v2.

1. Clone the repository and enter its root.
2. Copy `.env.example` to `.env`. Keep local values local; never commit `.env`.
3. Start the stack:

   ```bash
   docker compose up --build
   ```

4. Open the web app at <http://localhost:3000>.
5. Open interactive API docs at <http://localhost:8000/docs>.
6. Check API liveness at <http://localhost:8000/health>.

Stop with `docker compose down`. To delete local database data, use `docker compose down -v`.

## Tests and quality checks

Backend:

```bash
cd apps/api
python -m venv .venv
# Activate the environment, then:
pip install -r requirements.txt
ruff check app tests
pytest
```

Frontend:

```bash
cd apps/web
npm install
npm run lint
npm run typecheck
npm test
```

Run Playwright against a running stack before treating the browser workflows as verified:

```bash
npm run e2e
```

GitHub Actions runs backend lint/tests and frontend lint/typecheck/tests on pushes and pull requests. The E2E job also builds and starts the Compose stack.

## Project structure

```text
apps/web/        Next.js UI and client-side API workflows
apps/api/app/    FastAPI routes, schemas, models, settings and services
apps/api/alembic/ Versioned database migrations
apps/api/tests/  Backend tests
docs/            Architecture, API, database, AI and deployment docs
.github/         Continuous integration
```

## AI and privacy

The provider contract is defined in `app/services/ai/base.py`; the OpenAI-compatible adapter reads endpoint, key and model identifiers from environment settings. With `AI_PROVIDER=none`, the app uses a local baseline for job analysis and matching; semantic RAG is unavailable until a provider is configured and the CV is re-indexed.

Treat job descriptions and CV text as untrusted input. Model output is validated with Pydantic. RAG prompts require evidence-only answers and the API returns retrieved chunks alongside the answer. These controls reduce, but cannot eliminate, hallucinations. Users should verify claims before using them in applications.

## Security notes

- Passwords are hashed with Argon2; plaintext passwords are never persisted.
- Protected resources are scoped to the authenticated user's UUID. Foreign application IDs return 404.
- JWT and provider secrets are environment-driven; production rejects the default JWT secret and weak secret lengths.
- Uploads validate extension, declared MIME type, PDF signature, size and parsing.
- Logs contain request metadata, not request bodies, passwords, tokens or CV text.
- Production still requires HTTPS, a strong secret, exact CORS origins, backup/restore testing, token-storage hardening, rate limiting and a privacy/retention policy.

## Roadmap

1. Foundation, Docker and health checks.
2. Authentication, ownership, application CRUD and metrics.
3. Secure PDF upload and parsing.
4. Structured job analysis and deterministic matching.
5. Provider-backed embeddings, pgvector retrieval and evidence-grounded RAG.
6. Security review, broader automated tests, CI and observability.
7. UI polish, Playwright E2E coverage, verified screenshots and deployment guide.

## License

MIT. See [LICENSE](LICENSE).
