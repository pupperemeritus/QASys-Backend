from functools import lru_cache

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, db
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from qasys.config import settings

from qasys.utils.db_storage_helpers import get_user_vector_db_path

security = HTTPBearer()


@lru_cache()
def get_openai_api_key():
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not found")
    return settings.OPENAI_API_KEY


@lru_cache()
def get_embedding_model(api_key: str = Depends(get_openai_api_key)):
    return OpenAIEmbeddings(openai_api_key=api_key)


@lru_cache()
def get_llm(api_key: str = Depends(get_openai_api_key)):
    return ChatOpenAI(temperature=0, openai_api_key=api_key)


@lru_cache()
def get_vector_store(embedding_model=Depends(get_embedding_model)):
    return Chroma(embedding_function=embedding_model)


async def get_user_context(user_id: str = None):
    if not user_id:
        return ""
    try:
        ref = db.reference(settings.FIREBASE_MESSAGES_PATH.format(uid=user_id))
        messages = ref.get()
        return "\n".join(messages) if messages else ""
    except Exception as e:
        print(f"Error fetching user context: {e}")
        return ""


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials:
        token = credentials.credentials
        try:
            return auth.verify_id_token(token)
        except Exception as e:
            print(f"Token verification failed: {e}")
    raise HTTPException(status_code=401, detail="Invalid authentication credentials")


def get_current_user_id(token: dict = Depends(verify_token)):
    if token and "uid" in token:
        return token["uid"]
    raise HTTPException(status_code=401, detail="Invalid authentication credentials")
