# Architecture

## Runtime components

- **Next.js web** renders the responsive workspace. The client calls the API over HTTP/JSON; it does not connect to PostgreSQL directly.
- **FastAPI** owns request validation, authentication dependencies, authorization, API errors and OpenAPI documentation.
- **Pydantic schemas** validate inputs and outputs.
- **SQLAlchemy** maps domain entities to PostgreSQL. FastAPI dependency injection provides request-scoped sessions.
- **Alembic** versions schema changes. The API container runs `alembic upgrade head` before Uvicorn starts.
- **Services** implement document parsing, job extraction, matching and retrieval. AI provider interfaces keep external model APIs out of route handlers.
- **PostgreSQL** is the source of truth. `pgvector` stores CV chunk embeddings; vector queries are scoped by authenticated user ID.

## Request flow

1. The browser submits JSON or a PDF upload to FastAPI.
2. Pydantic validates JSON; upload handling checks extension, MIME, PDF signature, size and parseability.
3. `get_current_user` validates the bearer token and loads the user.
4. Resource queries include the owner UUID. Foreign or nonexistent application IDs return 404.
5. Services execute deterministic rules or call the configured AI adapter.
6. SQLAlchemy commits data; Pydantic response models shape the result.

## Authentication and security boundaries

Passwords are hashed using Argon2 via `pwdlib`. Login issues a signed JWT with a subject UUID and expiration. The web MVP keeps the token in `sessionStorage`; this is convenient but exposed to same-origin script execution. A hardened production design should use an HttpOnly, Secure, SameSite cookie through a BFF/session layer and assess CSRF protections. Production requires a non-default JWT secret and exact CORS origins.

## Observability

Middleware attaches a request ID, logs method, path, status and duration, and returns the ID in `X-Request-ID`. Request bodies, CV content, tokens and passwords are intentionally not logged. `/health` reports API liveness, not full database readiness.

## Trade-offs

The initial matching algorithm is transparent and cheap but relies on keyword/text signals, not semantic understanding. It is not a validated hiring prediction. Provider-backed RAG is optional; without provider credentials, PDF parsing and deterministic matching work, but embeddings and evidence Q&A are unavailable.
