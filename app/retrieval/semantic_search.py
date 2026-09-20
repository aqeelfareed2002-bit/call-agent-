from sqlalchemy.orm import Session

from app.database.modal import DocumentChunk
from app.ingestion.embedder import generate_embeddings


def semantic_search(
    db: Session,
    query: str,
    top_k: int = 10,
):
    # Generate embedding for the user's question
    query_embedding = generate_embeddings([query])[0]

    # Search using pgvector cosine distance
    chunks = (
        db.query(DocumentChunk)
        .order_by(
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            )
        )
        .limit(top_k)
        .all()
    )

    return chunks