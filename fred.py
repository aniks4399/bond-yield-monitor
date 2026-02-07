import requests
import pandas as pd
import boto3
import os

url = "https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key=e6e088f7ab2e539f3ea84cb5f14fdad1&file_type=json"

# 1. Make the request to the URL
response = requests.get(url)

# 2. Convert the response to JSON
data = response.json()

df=pd.DataFrame(data['observations'])
df.head()
df1=df.copy()
df1=df1[df1['value'] != '.']
df1
df2=df1.to_csv('bonds_data.csv', index=False)
bd=pd.read_csv('bonds_data.csv')
bd.head()
ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
s3=boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)
print("Connection is successful!")
# Upload the file
# Syntax: s3.upload_file(Source_File, Bucket_Name, Cloud_File_Name)

s3.upload_file('bonds_data.csv', 'bonds-data-anirudha-4399', 'bonds_data_cloud.csv')

print("Upload successful! Check your AWS Console.")