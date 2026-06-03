import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
fred_key = os.getenv("FRED_API_KEY")
url = f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={fred_key}&file_type=json"

# Add a User-Agent header so the cloud runner doesn't get blocked
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 1. Make the request to the URL using the browser header
response = requests.get(url, headers=headers)

# 2. Convert the response to JSON
data = response.json()

df = pd.DataFrame(data['observations'])

# Clean out the missing '.' data rows properly
df1 = df.loc[df['value'] != '.', ['date', 'value']].copy()

# Save cleanly to CSV
df1.to_csv('bonds_data.csv', index=False)

bd = pd.read_csv('bonds_data.csv')
print(bd.head())