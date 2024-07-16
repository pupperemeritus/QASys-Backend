import os
from typing import Optional

import dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings

dotenv.load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "LangChain Q&A FastAPI"
    DEBUG: bool = False

    # Database configurations
    FIREBASE_DATABASE_URL: str = os.getenv("FIREBASE_DATABASE_URL")
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH")

    # Vector DB configurations
    VECTOR_DB_TYPE: str = os.getenv(
        "VECTOR_DB_TYPE", "chroma"
    )  # e.g., "chroma", "pinecone", etc.
    VECTOR_DB_URL: Optional[str] = os.getenv(
        "VECTOR_DB_URL"
    )  # For cloud-hosted vector DBs
    VECTOR_DB_API_KEY: Optional[SecretStr] = os.getenv("VECTOR_DB_API_KEY")

    # Storage configurations
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")
    STORAGE_BUCKET: Optional[str] = os.getenv("STORAGE_BUCKET")
    PDF_STORAGE_PATH: str = os.getenv("PDF_STORAGE_PATH", "pdfs")

    # LangChain configurations
    OPENAI_API_KEY: SecretStr

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
