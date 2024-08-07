from enum import Enum

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", str_max_length=1000
    )
    APP_NAME: str = Field("LangChain Q&A FastAPI")
    DEBUG: bool = Field(False)
    PROJECT_ID: str

    # Database configurations
    FIREBASE_CREDENTIALS_FILENAME: SecretStr
    FIREBASE_MESSAGES_PATH: str

    # Vector DB configurations
    VECTOR_DB_TYPE: str = Field("chroma")

    # Storage configurations
    STORAGE_TYPE: StorageType = StorageType.LOCAL
    match STORAGE_TYPE:
        case StorageType.LOCAL:
            PDF_STORAGE_PATH: str = Field()
        case StorageType.GCP | StorageType.AWS | StorageType.AZURE:
            STORAGE_BUCKET: str = Field()
        case StorageType.AZURE:
            AZURE_CONNECTION_STRING: str = Field()

    # LangChain configurations
    MODEL_PROVIDER: ModelProvider = ModelProvider.OLLAMA

    match MODEL_PROVIDER:
        case MODEL_PROVIDER.OPENAI:
            # OpenAI settings
            OPENAI_API_KEY: SecretStr = Field()
            OPENAI_LLM_MODEL_NAME: str = Field("gpt-3.5-turbo")
            OPENAI_EMBEDDINGS_MODEL_NAME: str = Field("text-embedding-ada-002")
        case MODEL_PROVIDER.OLLAMA:
            # Ollama settings
            OLLAMA_LLM_MODEL_NAME: str = Field("llama3-chatqa")
            OLLAMA_EMBEDDINGS_MODEL_NAME: str = Field("all-minilm")
        case MODEL_PROVIDER.HUGGINGFACE:
            # HuggingFace settings
            HF_LLM_MODEL_NAME: str = Field("sentence-transformers/all-MiniLM-L6-v2")
            HF_EMBEDDINGS_MODEL_NAME: str = Field(
                "sentence-transformers/all-mpnet-base-v2"
            )


settings = Settings()
