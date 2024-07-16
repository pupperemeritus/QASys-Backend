import os
import shutil
import tempfile

from qasys.config import settings


def get_user_pdf_storage_path(user_id):
    base_path = settings.PDF_STORAGE_PATH
    return os.path.join(base_path, user_id)


def get_user_vector_db_path(user_id):
    base_path = settings.VECTOR_DB_PATH
    return os.path.join(base_path, user_id)


def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_temp_file(content):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(content)
    temp_file.close()
    return temp_file.name


def remove_temp_file(file_path):
    if os.path.exists(file_path):
        os.unlink(file_path)


def clear_user_data(user_id):
    pdf_path = get_user_pdf_storage_path(user_id)
    vector_db_path = get_user_vector_db_path(user_id)

    if os.path.exists(pdf_path):
        shutil.rmtree(pdf_path)
    if os.path.exists(vector_db_path):
        shutil.rmtree(vector_db_path)
