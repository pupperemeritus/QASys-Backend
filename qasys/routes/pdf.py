from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from qasys.core.pdf_processor import process_pdf
from qasys.core.vector_store import create_vector_store
from qasys.dependencies import get_embedding_model, get_user_vector_store, get_current_user_id
from qasys.utils.db_storage_helpers import create_temp_file, remove_temp_file

router = APIRouter()


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    embedding_model=Depends(get_embedding_model),
    vector_store=Depends(get_user_vector_store),
    user_id: str = Depends(get_current_user_id),
):
    try:
        temp_file_path = create_temp_file(await file.read())
        pages = process_pdf(temp_file_path)
        vector_store.add_documents(pages)
        remove_temp_file(temp_file_path)
        return {"message": "PDF processed and added to vector store successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
