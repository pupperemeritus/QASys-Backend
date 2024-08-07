from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from langchain.schema.vectorstore import VectorStore

from qasys.core.pdf_processor import process_pdf
from qasys.dependencies import get_authenticated_storage, get_storage, get_vector_store
from qasys.utils.storage import AuthenticatedStorage

router = APIRouter()


@router.post("/upload")
async def upload_pdf(
    file: UploadFile,
    request: Request,
    vector_store: VectorStore = Depends(get_vector_store),
):
    try:
        user_id = request.state.user_id
        file_content = file.file
        basic_storage = get_storage()
        storage = AuthenticatedStorage(basic_storage, user_id)
        file_path = storage.save_file(file.filename, file_content)
        file_binary = storage.get_file(file_path)
        pages = process_pdf(file_binary)
        vector_store.add_documents(pages)
        storage.delete_file(user_id, file_path)
        return JSONResponse(
            {
                "message": "PDF processed and added to vector store successfully",
            }
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
