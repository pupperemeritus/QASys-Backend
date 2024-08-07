from typing import Literal, LiteralString

from fastapi import Depends, HTTPException
from firebase_admin import auth, db
from langchain.llms.base import BaseLanguageModel
from langchain.schema.embeddings import Embeddings
from langchain_community.vectorstores import Chroma
from langchain_huggingface.chat_models import ChatHuggingFace
from langchain_huggingface.llms import HuggingFacePipeline
from langchain_ollama.chat_models import ChatOllama
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from qasys.config import ModelProvider, StorageType, settings
from qasys.utils.storage import (
    AuthenticatedStorage,
    AWSStorage,
    AzureStorage,
    GCPStorage,
    LocalStorage,
)


def get_openai_api_key():
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not found")
    return settings.OPENAI_API_KEY


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
            )
        case ModelProvider.HUGGINGFACE:
            return ChatHuggingFace(model_name=settings.HF_EMBEDDINGS_MODEL_NAME)
        case _:
            raise ValueError(f"Unsupported model provider: {settings.MODEL_PROVIDER}")


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


def get_llm() -> BaseLanguageModel:
    match settings.MODEL_PROVIDER:
        case ModelProvider.OPENAI:
            return ChatOpenAI(
                model=settings.OPENAI_LLM_MODEL_NAME,
                api_key=settings.OPENAI_API_KEY,
            )
        case ModelProvider.OLLAMA:
            return ChatOllama(
                model=settings.OLLAMA_LLM_MODEL_NAME,
            )
        case ModelProvider.HUGGINGFACE:
            tokenizer = AutoTokenizer.from_pretrained(settings.HF_LLM_MODEL_NAME)
            model = AutoModelForCausalLM.from_pretrained(settings.HF_LLM_MODEL_NAME)
            pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
            return HuggingFacePipeline(pipeline=pipe)
        case _:
            raise ValueError(f"Unsupported model provider: {settings.MODEL_PROVIDER}")


def get_vector_store(embedding_model=Depends(get_embedding_model)) -> Chroma:
    return Chroma(embedding_function=embedding_model)


async def verify_token(token: str):
    try:
        split_token = token.split("Bearer ")[-1]
        decoded_token = auth.verify_id_token(id_token=split_token)
        return decoded_token["uid"]
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Invalid or expired token: {str(e)}"
        )


async def get_user_context(user_id: str) -> LiteralString | Literal[""]:
    if not user_id:
        return ""
    try:
        ref = db.reference(settings.FIREBASE_MESSAGES_PATH.format(uid=user_id))
        messages = ref.get()
        return "\n".join(messages) if messages else ""
    except Exception as e:
        return ""


def get_authenticated_storage(user_id):
    base_storage = get_storage()
    return AuthenticatedStorage(base_storage, user_id)
