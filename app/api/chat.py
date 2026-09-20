from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.retrieval.pipeline import answer_question


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    question: str
    top_k: int = 5


@router.post("/")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    answer = answer_question(
        db=db,
        question=request.question,
        top_k=request.top_k
    )

    return {
        "question": request.question,
        "answer": answer
    }