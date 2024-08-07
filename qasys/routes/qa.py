from fastapi import APIRouter, Depends, HTTPException, Request
from langchain.schema.language_model import BaseLanguageModel
from pydantic import BaseModel

from qasys.core import vector_store
from qasys.core.qa_system import create_qa_system
from qasys.dependencies import get_llm, get_user_context, get_vector_store

router = APIRouter()


class Query(BaseModel):
    question: str


@router.post("/ask")
async def ask_question(
    query: Query,
    request: Request,
    llm: BaseLanguageModel = Depends(get_llm),
    vector_store: vector_store.Chroma = Depends(get_vector_store),
):
    try:
        qa_system = create_qa_system(vector_store, llm)
        user_id = request.state.user_id
        user_context = await get_user_context(user_id)
        context = f"Previous context: {user_context}\n\nQuestion: {query.question}"
        response = qa_system.invoke(context)
        return {"answer": response}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
