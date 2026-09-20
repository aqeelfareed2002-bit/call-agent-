from sqlalchemy.orm import Session

from app.database.modal import (
    Document,
    DocumentChunk,
)


def save_document(
    db: Session,
    filename: str,
    file_path: str,
    file_type: str,
    chunks: list[str],
    embeddings: list[list[float]],
):

    document = Document(
        filename=filename,
        file_path=file_path,
        file_type=file_type,
    )

    db.add(document)

    db.flush()

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):

        document_chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=index,
            content=chunk,
            embedding=embedding,
        )

        db.add(document_chunk)

    db.commit()

    db.refresh(document)

    return document