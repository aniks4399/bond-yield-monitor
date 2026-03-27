import requests
import pandas as pd
import boto3
import os
from dotenv import load_dotenv

load_dotenv()
fred_key=os.getenv("FRED_API_KEY")
url = f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={fred_key}&file_type=json"

# 1. Make the request to the URL
response = requests.get(url)

# 2. Convert the response to JSON
data = response.json()

df=pd.DataFrame(data['observations'])
df.head()
df1=df.copy()
#df1=df1[df1['value'] != '.']
#df1=df1[['date','value']]
df1=df1.loc[df1['value']!='.',['date','value']]
df2=df1.to_csv('bonds_data.csv', index=False)
bd=pd.read_csv('bonds_data.csv')
bd.head()
AWS_ACCESS_KEY_ID = os.environ.get("ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.environ.get("SECRET_KEY")
s3=boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
print(df1)
print("Connection is successful!")
# Upload the file
# Syntax: s3.upload_file(Source_File, Bucket_Name, Cloud_File_Name)

s3.upload_file('bonds_data.csv', 'bonds-data-anirudha-4399', 'bonds_data_cloud.csv')

print("Upload successful! Check your AWS Console.")     
