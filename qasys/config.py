from enum import Enum
from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class ModelProvider(str, Enum):
    OPENAI: str = "openai"
    OLLAMA: str = "ollama"
    HUGGINGFACE: str = "huggingface"


class StorageType(str, Enum):
    LOCAL: str = "local"
    GCP: str = "GCP"
    AWS: str = "AWS"
    AZURE: str = "Azure"


class Settings(BaseSettings):
    APP_NAME: str = "LangChain Q&A FastAPI"
    DEBUG: bool = False

    # Database configurations
    FIREBASE_CREDENTIALS_PATH: SecretStr

    # Vector DB configurations
    VECTOR_DB_TYPE: str = "chroma"

    # Storage configurations
    STORAGE_TYPE: StorageType = StorageType.LOCAL
    match STORAGE_TYPE:
        case StorageType.LOCAL:
            PDF_STORAGE_PATH: str = "data/pdfs"
        case StorageType.GCP | StorageType.AWS | StorageType.AZURE:
            STORAGE_BUCKET: str
        case StorageType.AZURE:
            AZURE_CONNECTION_STRING: str

    # LangChain configurations
    MODEL_PROVIDER: ModelProvider = ModelProvider.OLLAMA

    match MODEL_PROVIDER:
        case MODEL_PROVIDER.OPENAI:
            # OpenAI settings
            OPENAI_API_KEY: SecretStr
            OPENAI_LLM_MODEL_NAME: str = "gpt-3.5-turbo"
            OPENAI_EMBEDDINGS_MODEL_NAME: str = "text-embedding-ada-002"
        case MODEL_PROVIDER.OLLAMA:
            # Ollama settings
            OLLAMA_API_BASE: str = "http://localhost:11435/v1"
            OLLAMA_LLM_MODEL_NAME: str = "llama3-chatqa"
            OLLAMA_EMBEDDINGS_MODEL_NAME: str = "all-minilm"
        case MODEL_PROVIDER.HUGGINGFACE:
            # HuggingFace settings
            HF_LLM_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
            HF_EMBEDDINGS_MODEL_NAME: str = "sentence-transformers/all-mpnet-base-v2"

    class Config:
        env_file = ".env"
        case_sensitive = True
        use_enum_values = True


settings = Settings()
