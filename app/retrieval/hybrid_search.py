from sqlalchemy.orm import Session

from app.retrieval.semantic_search import semantic_search
from app.retrieval.keyword_search import keyword_search


def hybrid_search(
    db: Session,
    query: str,
    top_k: int = 5,
):
    candidate_k = top_k * 2

    print("\n" + "=" * 60)
    print("HYBRID SEARCH")
    print("QUERY:", query)
    print("=" * 60)

    # 1. Semantic search
    semantic_results = semantic_search(
        db=db,
        query=query,
        top_k=candidate_k,
    )

    print("\n--- SEMANTIC SEARCH RESULTS ---")

    for rank, chunk in enumerate(semantic_results, start=1):
        print(f"\nRank {rank}")
        print(f"Chunk ID: {chunk.id}")
        print(f"Content: {chunk.content[:200]}")

    # 2. Keyword search
    keyword_results = keyword_search(
        db=db,
        query=query,
        top_k=candidate_k,
    )

    print("\n--- KEYWORD SEARCH RESULTS ---")

    for rank, chunk in enumerate(keyword_results, start=1):
        print(f"\nRank {rank}")
        print(f"Chunk ID: {chunk.id}")
        print(f"Content: {chunk.content[:200]}")

    # 3. RRF fusion
    rrf_scores = {}
    k = 60

    for rank, chunk in enumerate(semantic_results, start=1):

        score = 1 / (k + rank)

        rrf_scores[chunk.id] = (
            rrf_scores.get(chunk.id, 0) + score
        )

    for rank, chunk in enumerate(keyword_results, start=1):

        score = 1 / (k + rank)

        rrf_scores[chunk.id] = (
            rrf_scores.get(chunk.id, 0) + score
        )

    # Combine unique chunks
    chunk_map = {}

    for chunk in semantic_results:
        chunk_map[chunk.id] = chunk

    for chunk in keyword_results:
        chunk_map[chunk.id] = chunk

    # Sort by combined RRF score
    ranked_chunks = sorted(
        chunk_map.values(),
        key=lambda chunk: rrf_scores[chunk.id],
        reverse=True,
    )

    final_chunks = ranked_chunks[:top_k]

    print("\n--- FINAL HYBRID RESULTS ---")

    for rank, chunk in enumerate(final_chunks, start=1):
        print(f"\nRank {rank}")
        print(f"Chunk ID: {chunk.id}")
        print(f"RRF Score: {rrf_scores[chunk.id]:.6f}")
        print(f"Content: {chunk.content[:200]}")

    print("\n" + "=" * 60)

    return final_chunks