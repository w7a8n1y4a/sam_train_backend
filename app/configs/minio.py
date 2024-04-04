from minio import Minio

from app import settings


minio_client = Minio(
    endpoint=settings.minio_host,
    access_key=settings.bucket_access_token,
    secret_key=settings.bucket_secret_key,
    secure=settings.minio_host_secure,
)

bucket_name = settings.bucket_name
