import io
import os
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime
from typing import BinaryIO, List

import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcp_storage


class Storage(ABC):
    @abstractmethod
    def save_file(self, file_name: str, file_content: BinaryIO) -> str:
        """Save a file and return its path or identifier"""
        pass

    @abstractmethod
    def get_file(self, file_path: str) -> BinaryIO:
        """Retrieve a file by its path or identifier"""
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """Delete a file by its path or identifier"""
        pass

    @abstractmethod
    def list_files(self, directory: str = "") -> List[str]:
        """List files in a directory"""
        pass

    @abstractmethod
    def get_file_metadata(self, file_path: str) -> dict:
        """Get metadata of a file"""
        pass


class LocalStorage(Storage):
    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def save_file(self, file_name: str, file_content: BinaryIO) -> str:
        file_path = os.path.join(self.base_path, file_name)
        with open(file_path, "wb") as f:
            f.write(file_content.read())
        return file_path

    def get_file(self, file_path: str) -> BinaryIO:
        return open(file_path, "rb")

    def delete_file(self, file_path: str) -> bool:
        try:
            os.remove(file_path)
            return True
        except OSError:
            return False

    def list_files(self, directory: str = "") -> List[str]:
        dir_path = os.path.join(self.base_path, directory)
        return [
            f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))
        ]

    def get_file_metadata(self, file_path: str) -> dict:
        stats = os.stat(file_path)
        return {
            "size": stats.st_size,
            "created_at": datetime.fromtimestamp(stats.st_ctime),
            "modified_at": datetime.fromtimestamp(stats.st_mtime),
        }


class GCPStorage(Storage):
    def __init__(self, bucket_name: str):
        self.client = gcp_storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def save_file(self, file_name: str, file_content: BinaryIO) -> str:
        blob = self.bucket.blob(file_name)
        blob.upload_from_file(file_content)
        return file_name

    def get_file(self, file_path: str) -> BinaryIO:
        blob = self.bucket.blob(file_path)
        file_obj = io.BytesIO()
        blob.download_to_file(file_obj)
        file_obj.seek(0)
        return file_obj

    def delete_file(self, file_path: str) -> bool:
        blob = self.bucket.blob(file_path)
        blob.delete()
        return True

    def list_files(self, directory: str = "") -> List[str]:
        return [blob.name for blob in self.bucket.list_blobs(prefix=directory)]

    def get_file_metadata(self, file_path: str) -> dict:
        blob = self.bucket.get_blob(file_path)
        return {
            "size": blob.size,
            "created_at": blob.time_created,
            "modified_at": blob.updated,
        }


class AWSStorage(Storage):
    def __init__(self, bucket_name: str):
        self.s3 = boto3.client("s3")
        self.bucket_name = bucket_name

    def save_file(self, file_name: str, file_content: BinaryIO) -> str:
        self.s3.upload_fileobj(file_content, self.bucket_name, file_name)
        return file_name

    def get_file(self, file_path: str) -> BinaryIO:
        file_obj = io.BytesIO()
        self.s3.download_fileobj(self.bucket_name, file_path, file_obj)
        file_obj.seek(0)
        return file_obj

    def delete_file(self, file_path: str) -> bool:
        self.s3.delete_object(Bucket=self.bucket_name, Key=file_path)
        return True

    def list_files(self, directory: str = "") -> List[str]:
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=directory)
        return [obj["Key"] for obj in response.get("Contents", [])]

    def get_file_metadata(self, file_path: str) -> dict:
        response = self.s3.head_object(Bucket=self.bucket_name, Key=file_path)
        return {
            "size": response["ContentLength"],
            "created_at": response["LastModified"],
            "modified_at": response["LastModified"],
        }


class AzureStorage(Storage):
    def __init__(self, connection_string: str, container_name: str):
        self.blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        self.container_client = self.blob_service_client.get_container_client(
            container_name
        )

    def save_file(self, file_name: str, file_content: BinaryIO) -> str:
        blob_client = self.container_client.get_blob_client(file_name)
        blob_client.upload_blob(file_content)
        return file_name

    def get_file(self, file_path: str) -> BinaryIO:
        blob_client = self.container_client.get_blob_client(file_path)
        stream = io.BytesIO()
        blob_client.download_blob().readinto(stream)
        stream.seek(0)
        return stream

    def delete_file(self, file_path: str) -> bool:
        blob_client = self.container_client.get_blob_client(file_path)
        blob_client.delete_blob()
        return True

    def list_files(self, directory: str = "") -> List[str]:
        return [
            blob.name
            for blob in self.container_client.list_blobs(name_starts_with=directory)
        ]

    def get_file_metadata(self, file_path: str) -> dict:
        blob_client = self.container_client.get_blob_client(file_path)
        properties = blob_client.get_blob_properties()
        return {
            "size": properties.size,
            "created_at": properties.creation_time,
            "modified_at": properties.last_modified,
        }


class AuthenticatedStorage:
    def __init__(self, storage: Storage):
        self.storage = storage

    def _get_user_path(self, user_id: str, file_path: str) -> str:
        return f"users/{user_id}/{file_path}"

    def save_file(self, user_id: str, file_name: str, file_content: BinaryIO) -> str:
        return self.storage.save_file(
            self._get_user_path(user_id, file_name), file_content
        )

    def get_file(self, user_id: str, file_path: str) -> BinaryIO:
        return self.storage.get_file(self._get_user_path(user_id, file_path))

    def delete_file(self, user_id: str, file_path: str) -> bool:
        return self.storage.delete_file(self._get_user_path(user_id, file_path))

    def list_files(self, user_id: str, directory: str = "") -> List[str]:
        return self.storage.list_files(self._get_user_path(user_id, directory))

    def get_file_metadata(self, user_id: str, file_path: str) -> dict:
        return self.storage.get_file_metadata(self._get_user_path(user_id, file_path))


def get_authenticated_storage():
    base_storage = get_storage()
    return AuthenticatedStorage(base_storage)


def create_temp_file(content):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(content)
    temp_file.close()
    return temp_file.name


def remove_temp_file(file_path):
    if os.path.exists(file_path):
        os.unlink(file_path)
