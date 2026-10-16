# API reference

FastAPI's generated interactive reference is available at `/docs`; OpenAPI JSON is at `/openapi.json`.

## Health
- `GET /health` — process liveness response.

## Auth
- `POST /auth/register` — create an account. Password must be at least 12 characters.
- `POST /auth/login` — returns a bearer access token.
- `GET /auth/me` — current authenticated user.

## Applications
- `POST /applications` — create a record.
- `GET /applications` — list only the current user's records.
- `GET /applications/{application_id}` — retrieve an owned record.
- `PATCH /applications/{application_id}` — update provided fields.
- `DELETE /applications/{application_id}` — delete an owned record.
- `GET /dashboard/stats` — counts and interview conversion from persisted records.

Application statuses are `SAVED`, `APPLIED`, `INTERVIEW`, `OFFER`, and `REJECTED`. Protected endpoints use `Authorization: Bearer <token>`. Foreign resources return 404.

## Resume and analysis
- `POST /resume` — multipart field `file`, PDF only, limited by `MAX_RESUME_SIZE_MB`.
- `GET /resume` — get the current user's latest CV text and metadata.
- `DELETE /resume` — delete the current user's CV.
- `POST /job-analyzer` — JSON body `{ "description": "..." }`; returns typed requirements.
- `POST /applications/{application_id}/analyze` — requires an owned application with a description and an uploaded CV.
- `GET /applications/{application_id}/analysis` — latest analysis for an owned application.
- `POST /resume/ask` — requires a configured provider and indexed chunks; returns answer plus supporting evidence.

## Common errors
401 missing/invalid credentials; 404 resource missing or not owned; 409 duplicate account or missing prerequisite; 413 oversized PDF; 415 unsupported/invalid file type; 422 invalid request or unparseable PDF; 502 provider/indexing failure; 503 RAG unavailable without a provider.
