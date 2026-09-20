from sqlalchemy.orm import Session

from app.retrieval.hybrid_search import hybrid_search
from app.retrieval.generator import generate_answer


def answer_question(
    db: Session,
    question: str,
    top_k: int = 5,
):
    # Step 1: Hybrid retrieval
    chunks = hybrid_search(
        db=db,
        query=question,
        top_k=top_k,
    )

    # Step 2: Generate answer using retrieved chunks
    answer = generate_answer(
        question=question,
        chunks=chunks,
    )

    return answer