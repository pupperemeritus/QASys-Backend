from fastapi import APIRouter, Depends, HTTPException
from langchain.schema.embeddings import Embeddings
from langchain.schema.language_model import BaseLanguageModel
from pydantic import BaseModel

from qasys.core import vector_store
from qasys.core.qa_system import create_qa_system
from qasys.dependencies import (
    get_current_user_id,
    get_embedding_model,
    get_llm,
    get_user_context,
    get_vector_store,
)

router = APIRouter()


class Query(BaseModel):
    question: str


@router.post("/ask")
async def ask_question(
    query: Query,
    llm: BaseLanguageModel = Depends(get_llm),
    vector_store: vector_store.Chroma = Depends(get_vector_store),
    user_context: str = Depends(get_user_context),
):
    try:
        qa_system = create_qa_system(vector_store, llm)
        context = f"Previous context: {user_context}\n\nQuestion: {query.question}"
        response = qa_system.run(context)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
