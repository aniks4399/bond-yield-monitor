import requests
import pandas as pd
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

df1.loc[df1['value'] != '.', ['date', 'value']]
df2 = df1.to_csv('bonds_data.csv', index=False)
bd = pd.read_csv('bonds_data.csv')
print(bd.head())
print(df1)
