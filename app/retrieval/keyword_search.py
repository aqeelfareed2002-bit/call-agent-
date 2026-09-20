from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.modal import DocumentChunk


def keyword_search(
    db: Session,
    query: str,
    top_k: int = 10,
):
    # Convert document content into a PostgreSQL text-search vector
    search_vector = func.to_tsvector(
        "english",
        DocumentChunk.content,
    )

    # Convert the user's query into a PostgreSQL search query
    search_query = func.plainto_tsquery(
        "english",
        query,
    )

    # Rank matching chunks according to keyword relevance
    chunks = (
        db.query(DocumentChunk)
        .filter(
            search_vector.op("@@")(search_query)
        )
        .order_by(
            func.ts_rank(
                search_vector,
                search_query,
            ).desc()
        )
        .limit(top_k)
        .all()
    )

    return chunks