from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.ingestion.uploader import save_uploaded_file
from app.ingestion.pdf_extractor import extract_text
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import generate_embeddings
from app.ingestion.storage import save_document


def ingest_document(
    db: Session,
    file: UploadFile,
):

    # 1. Save uploaded PDF

    file_path = save_uploaded_file(file)


    # 2. Extract text

    text = extract_text(file_path)

    if not text.strip():

        raise ValueError(
            "Could not extract text from PDF"
        )


    # 3. Create chunks

    chunks = chunk_text(text)

    if not chunks:

        raise ValueError(
            "No chunks were created"
        )


    # 4. Generate embeddings

    embeddings = generate_embeddings(
        chunks
    )


    # 5. Store everything in database

    document = save_document(
        db=db,
        filename=file.filename,
        file_path=file_path,
        file_type=file.content_type
        or "application/pdf",
        chunks=chunks,
        embeddings=embeddings,
    )


    # 6. Return useful information

    return {
        "document_id": document.id,
        "filename": document.filename,
        "file_path": document.file_path,
        "text_length": len(text),
        "chunks_created": len(chunks),
        "embeddings_created": len(embeddings),
        "embedding_dimension": (
            len(embeddings[0])
            if embeddings
            else 0
        ),
    }