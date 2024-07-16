from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from qasys.core.qa_system import create_qa_system
from qasys.dependencies import (
    get_embedding_model,
    get_llm,
    get_user_vector_store,
    get_user_context,
    get_current_user_id,
)

router = APIRouter()


class Query(BaseModel):
    question: str


@router.post("/ask")
async def ask_question(
    query: Query,
    embedding_model=Depends(get_embedding_model),
    llm=Depends(get_llm),
    vector_store=Depends(get_user_vector_store),
    user_context=Depends(get_user_context),
    user_id: str = Depends(get_current_user_id),
):
    try:
        qa_system = create_qa_system(vector_store, llm)
        context = f"Previous context: {user_context}\n\nQuestion: {query.question}"
        response = qa_system.run(context)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
