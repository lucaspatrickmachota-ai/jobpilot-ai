# Contributing to JobPilot AI

## Principles
- Keep business logic in focused services where practical.
- Keep database changes in Alembic migrations; do not use `create_all()` in production.
- Never commit API keys, JWT secrets, `.env` files, personal CVs or real user data.
- Do not fabricate application records or present mock data as live metrics.
- Scope every resource query to the authenticated owner.
- Keep deterministic scoring independent of LLM output and document scoring changes.
- RAG responses must return source evidence and disclose insufficient evidence.

## Local checks

Backend:
```bash
cd apps/api
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
npm run e2e # requires the app at localhost:3000 and API at localhost:8000
```

Full local stack:
```bash
docker compose up --build
```

## Pull requests
Describe the problem, implementation, security implications, migration impact and tests executed. Never claim a check passed unless it was actually run. Keep commits small and use conventional commit messages.
