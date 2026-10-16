"""Add pgvector-backed resume evidence chunks."""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "0003_resume_chunks"
down_revision = "0002_resumes_analyses"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "resume_chunks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("resume_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(length=2000), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("resume_id", "chunk_index", name="uq_resume_chunks_resume_index"),
    )
    op.create_index("ix_resume_chunks_resume_id", "resume_chunks", ["resume_id"])
    op.create_index("ix_resume_chunks_user_id", "resume_chunks", ["user_id"])
    op.execute("CREATE INDEX ix_resume_chunks_embedding_cosine ON resume_chunks USING hnsw (embedding vector_cosine_ops)")


def downgrade() -> None:
    op.drop_index("ix_resume_chunks_embedding_cosine", table_name="resume_chunks")
    op.drop_index("ix_resume_chunks_user_id", table_name="resume_chunks")
    op.drop_index("ix_resume_chunks_resume_id", table_name="resume_chunks")
    op.drop_table("resume_chunks")
    op.execute("DROP EXTENSION IF EXISTS vector")
