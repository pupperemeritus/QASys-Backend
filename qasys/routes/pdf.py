from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from langchain.schema.vectorstore import VectorStore
from langchain.schema.embeddings import Embeddings
from qasys.utils.storage import Storage
from qasys.core.pdf_processor import process_pdf
from qasys.core.vector_store import create_vector_store
from qasys.dependencies import (
    get_current_user_id,
    get_embedding_model,
    get_user_vector_store,
)
from qasys.utils.storage import get_authenticated_storage

router = APIRouter()


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    embedding_model: Embeddings = Depends(get_embedding_model),
    vector_store: VectorStore = Depends(get_user_vector_store),
    user_id: str = Depends(get_current_user_id),
    storage: Storage = Depends(get_authenticated_storage),
) -> dict:
    try:
        file_content = await file.read()
        file_path = storage.save_file(user_id, file.filename, file_content)
        pages = process_pdf(file_path, storage)
        vector_store.add_documents(pages)
        return {
            "message": "PDF processed and added to vector store successfully",
            "file_path": file_path,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
