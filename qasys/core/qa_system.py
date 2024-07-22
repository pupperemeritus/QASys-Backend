from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.llms.base import BaseLanguageModel
from langchain.vectorstores.base import VectorStore


def create_qa_system(retriever: VectorStore, llm: BaseLanguageModel) -> RetrievalQA:
    return RetrievalQA.from_chain_type(
        llm, chain_type="stuff", retriever=retriever.as_retriever()
    )
