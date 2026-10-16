# JobPilot AI

An explainable job-search workspace for tracking applications, analysing job descriptions, and comparing role requirements with evidence from a CV.

> **Project status:** initial public repository setup. The implementation is being published and validated incrementally; do not treat it as production-ready until CI and deployment checks pass.

## Planned stack

- **Web:** Next.js, React, TypeScript
- **API:** FastAPI, Pydantic, SQLAlchemy, Alembic
- **Data:** PostgreSQL and pgvector
- **Quality:** pytest, Vitest, GitHub Actions
- **Deployment:** Docker Compose

## Product principles

- Matching scores are deterministic and explainable; an LLM does not decide the final score.
- Application data must be scoped to the authenticated user.
- CV uploads must be validated and treated as sensitive data.
- AI/RAG responses should be grounded in retrieved CV evidence and disclose missing evidence.
- No fake dashboard records or fabricated metrics.

## Planned matching baseline

| Dimension | Weight |
|---|---:|
| Skills | 50% |
| Experience signals | 30% |
| Education signals | 10% |
| Language signals | 10% |

These are heuristic decision-support signals, not predictions of hiring outcomes.

## Development

The repository will include the web application, API, database migrations, tests, and deployment instructions as they are validated. Configuration belongs in environment variables; never commit real API keys, passwords, tokens, CVs, or other personal data.

## Roadmap

1. Repository foundation and health checks.
2. Authentication, application CRUD, ownership and dashboard metrics.
3. Secure PDF CV upload and parsing.
4. Job analysis and explainable matching.
5. Optional embeddings, pgvector retrieval and evidence-grounded RAG.
6. Security review, automated tests and CI.
7. UI polish, end-to-end testing and deployment verification.

## Security

If you discover a vulnerability, please do not publish secrets or sensitive user data in an issue. Report the issue privately to the repository owner.

## License

MIT (license file to follow).
