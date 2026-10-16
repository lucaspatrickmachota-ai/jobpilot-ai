# Deployment checklist

## Before deployment
1. Choose a host for the web/API containers and PostgreSQL with the `vector` extension.
2. Set `APP_ENV=production`, a unique `JWT_SECRET` of at least 32 random characters, and exact `CORS_ORIGINS`.
3. Set `DATABASE_URL` using a private database hostname and required TLS settings. URL-encode reserved password characters.
4. Confirm match weights are non-negative and sum to 1.0.
5. Keep `AI_PROVIDER=none` unless provider privacy terms have been reviewed and a valid API key/model is configured.
6. Run `alembic upgrade head`, then verify health and authenticated database-backed smoke tests.

## Container deployment
The supplied Compose file is for local development and exposes PostgreSQL on the host. In production, keep the database on private networking, use HTTPS at ingress, and manage secrets outside the repository. For multi-replica deployments, run migrations as a one-off release job to avoid races.

## Before real users
- Configure HTTPS, request body limits and rate limiting.
- Replace browser `sessionStorage` token storage with a secure cookie/BFF design and assess CSRF requirements.
- Configure backups and test restores.
- Establish CV retention/deletion policy, privacy notice and consent for external AI processing.
- Add alerting for failed health checks, elevated 5xx responses and database exhaustion.
- Run the full CI workflow, including Playwright, and review dependency vulnerabilities.

This checklist is not a claim that production deployment has already been completed.
