from fastapi import APIRouter, Depends, HTTPException, Request
from langchain.schema.vectorstore import VectorStore

from qasys.dependencies import (
    get_authenticated_storage,
    get_vector_store,
)
from qasys.utils.storage import AuthenticatedStorage

router = APIRouter()


@router.get("/me")
async def get_current_user(request: Request):
    user_id = request.state.user_id
    return {"user_id": user_id}


@router.post("/clear_data")
async def clear_user_data(
    request: Request,
    storage: AuthenticatedStorage = Depends(get_authenticated_storage),
    vector_store: VectorStore = Depends(get_vector_store),
):
    try:
        user_id = request.state.user_id
        files = storage.list_files(user_id)
        for file in files:
            storage.delete_file(user_id, file)

        vector_store.clear_user_data(user_id)

        return {"message": "User data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files")
async def list_user_files(
    request: Request,
    storage=Depends(get_authenticated_storage),
):
    try:
        user_id = request.state.user_id
        files = storage.list_files(user_id)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
