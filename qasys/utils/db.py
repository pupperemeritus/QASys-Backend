import os
import shutil

from qasys.config import settings


def get_user_vector_db_path(user_id):
    base_path = settings.VECTOR_DB_PATH
    return os.path.join(base_path, user_id)


def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def clear_user_vector_db(user_id):
    vector_db_path = get_user_vector_db_path(user_id)
    if os.path.exists(vector_db_path):
        shutil.rmtree(vector_db_path)


def clear_user_data(user_id):
    # Clear vector store data
    clear_user_vector_db(user_id)

    # Here you would add any other database-related cleanup
    # For example, if you're using a separate database for user data:
    # clear_user_database_entries(user_id)

    return {"message": "User database data cleared successfully"}
