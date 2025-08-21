import boto3
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET = os.getenv("AWS_BUCKET")

# Create boto3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# Test file
file_name = "test.txt"
with open(file_name, "w") as f:
    f.write("Hello, Secure File Transfer via QR Code!")

# Upload file
s3.upload_file(file_name, AWS_BUCKET, file_name)
print(f"✅ Uploaded {file_name} to bucket {AWS_BUCKET}")

# Generate presigned URL (valid 60 sec)
url = s3.generate_presigned_url(
    "get_object",
    Params={"Bucket": AWS_BUCKET, "Key": file_name},
    ExpiresIn=60
)
print("🔗 Presigned URL:", url)
