# AI system

## Pipeline
1. PDF bytes are validated and text is extracted with `pypdf`.
2. A local baseline extracts known skill names and requirement fields from job-description text.
3. When configured, an AI provider can return structured JSON validated with Pydantic.
4. A deterministic matching engine computes the score; no LLM chooses the final percentage.
5. Optional embeddings split CV text into overlapping chunks and store them in PostgreSQL/pgvector.
6. Questions are embedded and ranked by cosine distance, constrained to the authenticated user's chunks. The answer returns source evidence for inspection.

## Provider abstraction
`app/services/ai/base.py` defines `complete`, `extract_structured`, and `embed`. The OpenAI-compatible adapter reads endpoint, key, model, embedding model and timeout from environment settings. `AI_PROVIDER=none` disables provider calls; supported values are `openai` and `openai_compatible`.

The vector column is 1536 dimensions. If using another embedding model or dimensions, update model, migration, validation and index consistently before deployment.

## Explainable matching
Default weights are skills 50%, experience 30%, education 10%, and languages 10%. Skills use explicit aliases and word-boundary matching. The other components currently use textual phrase signals. These heuristics are reproducible but not statistically validated.

## RAG controls and privacy
The prompt instructs the model to answer only from supplied CV passages, avoid inventing employers, skills, dates or qualifications, and cite chunk UUIDs. Prompt instructions reduce risk but do not guarantee factuality. CV text is not logged. Provider requests occur only when configured. Production use should review provider retention terms, obtain consent, and implement retention/deletion policies.
