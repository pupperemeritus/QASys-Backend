from functools import lru_cache
from typing import Any, Dict, Literal, LiteralString, Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, db
from langchain.llms.base import BaseLanguageModel
from langchain.schema.embeddings import Embeddings
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain_community.llms.ollama import Ollama
from langchain_community.embeddings import OllamaEmbeddings, HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

from qasys.config import ModelProvider, StorageType, settings
from qasys.utils.storage import AWSStorage, AzureStorage, GCPStorage, LocalStorage

security = HTTPBearer()

device = "gpu" if torch.cuda.is_available() else "cpu"


@lru_cache()
def get_openai_api_key():
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not found")
    return settings.OPENAI_API_KEY


@lru_cache()
def get_embedding_model() -> Embeddings:
    match settings.MODEL_PROVIDER:
        case ModelProvider.OPENAI:
            return OpenAIEmbeddings(
                model=settings.OPENAI_EMBEDDINGS_MODEL_NAME,
                openai_api_key=settings.OPENAI_API_KEY,
            )
        case ModelProvider.OLLAMA:
            return OllamaEmbeddings(
                model=settings.OLLAMA_EMBEDDINGS_MODEL_NAME,
                base_url=settings.OLLAMA_API_BASE,
            )
        case ModelProvider.HUGGINGFACE:
            return HuggingFaceEmbeddings(
                model_name=settings.HF_EMBEDDINGS_MODEL_NAME, device=device
            )
        case _:
            raise ValueError(f"Unsupported model provider: {settings.MODEL_PROVIDER}")


@lru_cache()
def get_storage():
    match settings.STORAGE_TYPE:
        case StorageType.LOCAL:
            return LocalStorage(settings.PDF_STORAGE_PATH)
        case StorageType.GCP:
            return GCPStorage(settings.STORAGE_BUCKET)
        case StorageType.AWS:
            return AWSStorage(settings.STORAGE_BUCKET)
        case StorageType.AZURE:
            return AzureStorage(
                settings.AZURE_CONNECTION_STRING, settings.STORAGE_BUCKET
            )
        case _:
            raise ValueError(f"Unsupported storage type: {settings.STORAGE_TYPE}")


@lru_cache()
def get_llm() -> BaseLanguageModel:
    match settings.MODEL_PROVIDER:
        case ModelProvider.OPENAI:
            return ChatOpenAI(
                model=settings.OPENAI_LLM_MODEL_NAME,
                api_key=settings.OPENAI_API_KEY,
            )
        case ModelProvider.OLLAMA:
            return Ollama(
                model=settings.OLLAMA_LLM_MODEL_NAME,
                base_url=settings.OLLAMA_API_BASE,
            )
        case ModelProvider.HUGGINGFACE:
            tokenizer = AutoTokenizer.from_pretrained(settings.HF_LLM_MODEL_NAME)
            model = AutoModelForCausalLM.from_pretrained(settings.HF_LLM_MODEL_NAME)
            pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
            return HuggingFacePipeline(pipeline=pipe)
        case _:
            raise ValueError(f"Unsupported model provider: {settings.MODEL_PROVIDER}")


@lru_cache()
def get_vector_store(embedding_model=Depends(get_embedding_model)) -> Chroma:
    return Chroma(embedding_function=embedding_model)


async def get_user_context(user_id: str = None) -> LiteralString | Literal[""]:
    if not user_id:
        return ""
    try:
        ref = db.reference(settings.FIREBASE_MESSAGES_PATH.format(uid=user_id))
        messages = ref.get()
        return "\n".join(messages) if messages else ""
    except Exception as e:
        print(f"Error fetching user context: {e}")
        return ""


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[Dict]:
    if credentials:
        token = credentials.credentials
        try:
            return auth.verify_id_token(token)
        except Exception as e:
            print(f"Token verification failed: {e}")
    raise HTTPException(status_code=401, detail="Invalid authentication credentials")


def get_current_user_id(token: Dict = Depends(verify_token)) -> str:
    if token and "uid" in token:
        return token["uid"]
    raise HTTPException(status_code=401, detail="Invalid authentication credentials")
