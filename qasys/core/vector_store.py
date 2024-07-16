from typing import List, Type

from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores.base import VectorStore
from langchain_community.vectorstores import Chroma


def create_vector_store(
    documents: List[Document],
    embedding_model: Embeddings,
    vector_store_cls: Type[VectorStore] = Chroma,
) -> VectorStore:
    return vector_store_cls.from_documents(documents, embedding_model)
