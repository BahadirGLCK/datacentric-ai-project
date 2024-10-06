import boto3
from botocore.client import Config
from dotenv import load_dotenv
import os

class MinIOClient:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Access credentials and other configs from environment variables
        self.endpoint = os.getenv('MINIO_ENDPOINT')
        self.access_key = os.getenv('MINIO_ACCESS_KEY')
        self.secret_key = os.getenv('MINIO_SECRET_KEY')
        self.bucket_name = os.getenv('MINIO_IMAGE_BUCKET')

        # Initialize the MinIO client
        self.minio_client = boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4')
        )

    def upload_image(self, file_path: str, object_name: str):
        """
        Upload an image to MinIO.

        :param file_path: Local path of the image to upload.
        :param object_name: Name of the object in the MinIO bucket.
        :raises: Exception if upload fails.
        """
        try:
            with open(file_path, "rb") as file_data:
                self.minio_client.upload_fileobj(file_data, self.bucket_name, object_name)
                print(f"Successfully uploaded {object_name} to bucket {self.bucket_name}")
        except Exception as e:
            raise Exception(f"Failed to upload {object_name}: {str(e)}")

    def download_image(self, object_name: str, download_path: str):
        """
        Download an image from MinIO.

        :param object_name: Name of the object in the MinIO bucket.
        :param download_path: Local path where the downloaded image will be saved.
        :raises: Exception if download fails.
        """
        try:
            self.minio_client.download_file(self.bucket_name, object_name, download_path)
            print(f"Successfully downloaded {object_name} to {download_path}")
        except Exception as e:
            raise Exception(f"Failed to download {object_name}: {str(e)}")