import os
import tempfile
from typing import BinaryIO, List

from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader

from qasys.utils.storage import AuthenticatedStorage


def process_pdf(pdf_content: BinaryIO) -> List[Document]:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(pdf_content)
        temp_file_path = temp_file.name
    loader = PyPDFLoader(temp_file_path)
    pages = loader.load_and_split()
    os.remove(temp_file_path)
    return pages
