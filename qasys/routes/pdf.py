from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from langchain.schema.vectorstore import VectorStore

from qasys.core.pdf_processor import process_pdf
from qasys.dependencies import (
    get_vector_store,
    get_authenticated_storage,
)
from qasys.utils.storage import AuthenticatedStorage

router = APIRouter()


@router.post("/upload")
async def upload_pdf(
    file: UploadFile,
    request: Request,
    vector_store: VectorStore = Depends(get_vector_store),
    storage: AuthenticatedStorage = Depends(get_authenticated_storage),
) -> dict:
    try:
        user_id = request.state.user_id
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
