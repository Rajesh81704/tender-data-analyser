import boto3
import os
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables
load_dotenv('app/.env')

class S3Client:
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
            region_name=os.getenv("REGION_NAME", "us-east-1")
        )
        self.bucket_name = os.getenv("BUCKET_NAME")
    
    def upload_file(self, file_path, object_name=None):
        if object_name is None:
            object_name = os.path.basename(file_path)
        
        try:
            # Use multipart upload for large files (automatically handled by boto3)
            # boto3 automatically uses multipart for files > 8MB
            from boto3.s3.transfer import TransferConfig
            
            # Configure for large files
            config = TransferConfig(
                multipart_threshold=8 * 1024 * 1024,  # 8MB
                max_concurrency=10,
                multipart_chunksize=8 * 1024 * 1024,  # 8MB
                use_threads=True
            )
            
            self.client.upload_file(
                file_path, 
                self.bucket_name, 
                object_name,
                Config=config
            )
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
    
    def download_file(self, object_name, file_path):
        try:
            self.client.download_file(self.bucket_name, object_name, file_path)
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False
    
    def get_file_stream(self, object_name):
        """Stream file directly from S3 into memory as BytesIO object"""
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=object_name)
            return BytesIO(response['Body'].read())
        except Exception as e:
            print(f"Error streaming file: {e}")
            return None
    
    def delete_file(self, object_name):
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def list_files(self, prefix=''):
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            return [obj['Key'] for obj in response.get('Contents', [])]
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

# Singleton instance
s3_client = S3Client()
