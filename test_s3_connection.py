from app.api.utils.s3_client import s3_client

try:
    # Test listing files in the bucket
    files = s3_client.list_files()
    print(f"✓ S3 connection successful!")
    print(f"  Bucket: {s3_client.bucket_name}")
    print(f"  Files found: {len(files)}")
    if files:
        print(f"  Sample files: {files[:5]}")
except Exception as e:
    print(f"✗ S3 connection failed: {e}")
