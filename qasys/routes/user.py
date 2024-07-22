from fastapi import APIRouter, Depends, HTTPException
from langchain.schema.vectorstore import VectorStore

from qasys.dependencies import get_current_user_id, get_vector_store
from qasys.utils.storage import AuthenticatedStorage, get_authenticated_storage

router = APIRouter()


@router.get("/me")
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    return {"user_id": user_id}


@router.post("/clear_data")
async def clear_user_data(
    user_id: str = Depends(get_current_user_id),
    storage: AuthenticatedStorage = Depends(get_authenticated_storage),
    vector_store: VectorStore = Depends(get_vector_store),
):
    try:
        # Clear user's files
        files = storage.list_files(user_id)
        for file in files:
            storage.delete_file(user_id, file)

        # Here you would also clear other user data, such as from the vector store
        # This depends on how you've implemented your vector store
        # For example:
        vector_store.clear_user_data(user_id)

        return {"message": "User data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files")
async def list_user_files(
    user_id: str = Depends(get_current_user_id),
    storage=Depends(get_authenticated_storage),
):
    try:
        files = storage.list_files(user_id)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
