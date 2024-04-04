import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    """.env variables"""

    app_path = os.path.abspath(os.getcwd())

    debug: bool
    app_prefix: str
    api_v1_prefix: str
    project_name: str
    version: str
    description: str

    telegram_token: str
    model_id: str

    bucket_access_token: str
    bucket_secret_key: str
    bucket_name: str
    minio_host: str
    minio_host_secure: bool
