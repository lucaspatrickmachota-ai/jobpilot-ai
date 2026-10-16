# Database design

## Tables
- `users`: account email, password hash and timestamps.
- `applications`: company, position, URL, job description, status and owner UUID.
- `resumes`: current CV filename and extracted text, owned by a user.
- `job_analyses`: historical match scores, breakdown, matched/missing skills and explanation.
- `resume_chunks`: bounded text chunks with 1536-dimensional pgvector embeddings, source resume, owner and chunk order.

## Ownership and relationships
A user has many applications and resumes. An application has many analyses. A resume has many chunks. Foreign keys cascade deletes, and API retrieval always applies owner filters. Vector retrieval scopes by user ID and active resume ID.

## Migrations
- `0001_initial`: users and applications.
- `0002_resumes_analyses`: resumes and persisted analyses.
- `0003_resume_chunks`: enables pgvector and adds chunk storage and cosine index.

Alembic manages the production schema. Tests may create isolated SQLite tables with SQLAlchemy metadata; production startup uses versioned migrations.
