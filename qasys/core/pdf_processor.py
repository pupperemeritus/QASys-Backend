import os
import tempfile
from typing import List

from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader


def process_pdf(file) -> List[Document]:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(file.read())
    loader = PyPDFLoader(tmp_file.name)
    pages = loader.load_and_split()
    os.unlink(tmp_file.name)
    return pages
