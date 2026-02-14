import boto3
from botocore.client import Config
import os
ACCESS_KEY=os.environ.get("AWS_ACCESS_KEY_ID")
SECRET_KEY=os.environ.get("AWS_SECRET_ACCESS_KEY")
s3=boto3.client('s3', 
                aws_access_key_id=ACCESS_KEY, 
                aws_secret_access_key=SECRET_KEY,
                config=Config(signature_version='s3v4',
                region_name='eu-north-1')
                )
# 2. Define exactly what we want to share
BUCKET_NAME = "bonds-data-anirudha-4399"
FILE_KEY = "bonds_data_cloud.csv"
url=s3.generate_presigned_url(
    ClientMethod='get_object',
    Params={
        'Bucket':BUCKET_NAME,
        'Key':FILE_KEY
    },
    ExpiresIn=3600
)
print("--- COPY THIS LINK BELOW ---")
print(url)
print("----------------------------")
