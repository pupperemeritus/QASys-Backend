from typing import List

from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader

from qasys.utils.storage import Storage


def process_pdf(file_path: str, storage: Storage) -> List[Document]:
    with storage.get_file(file_path) as file:
        loader = PyPDFLoader(file)
        pages = loader.load_and_split()
    storage.delete_file(file_path)
    return pages
