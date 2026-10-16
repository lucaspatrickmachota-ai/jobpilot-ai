from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ResumeChunk
from app.services.ai.base import AIProvider


def index_resume_chunks(db: Session, *, resume_id: UUID, user_id: UUID, text: str, provider: AIProvider) -> int:
    from app.services.chunking import chunk_text

    chunks = chunk_text(text)
    vectors = provider.embed(chunks)
    if len(vectors) != len(chunks) or any(len(vector) != 1536 for vector in vectors):
        raise ValueError("Embedding dimensions must match the configured 1536-dimensional pgvector column")
    db.add_all([
        ResumeChunk(resume_id=resume_id, user_id=user_id, chunk_index=index, content=chunk, embedding=vector)
        for index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True))
    ])
    db.flush()
    return len(chunks)


def retrieve_resume_evidence(db: Session, *, user_id: UUID, resume_id: UUID, question: str, provider: AIProvider, limit: int = 4) -> list[ResumeChunk]:
    query_vectors = provider.embed([question])
    if len(query_vectors) != 1 or len(query_vectors[0]) != 1536:
        raise ValueError("Embedding dimensions must match the configured 1536-dimensional pgvector column")
    distance = ResumeChunk.embedding.cosine_distance(query_vectors[0])
    statement = select(ResumeChunk, distance.label("distance")).where(
        ResumeChunk.user_id == user_id, ResumeChunk.resume_id == resume_id
    ).order_by(distance).limit(limit)
    rows = db.execute(statement).all()
    return [chunk for chunk, cosine_distance in rows if cosine_distance <= 0.45]
