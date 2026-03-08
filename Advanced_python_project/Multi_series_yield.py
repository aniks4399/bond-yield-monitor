import requests
import pandas as pd
import matplotlib.pyplot as plt
import boto3
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()

series_ids=['DGS30','DGS10','DGS5','DGS2','DGS3MO']
all_bonds_data=[]
for maturity_id in series_ids:

    url=f"https://api.stlouisfed.org/fred/series/observations?series_id={maturity_id}&api_key=e6e088f7ab2e539f3ea84cb5f14fdad1&file_type=json"
    response=requests.get(url)
    data=response.json()
    print(f"Successfully pulled data from {maturity_id}")
    df=pd.DataFrame(data['observations'])
    df=df.loc[df['value']!='.',['date','value']]
    df['series_id']=maturity_id
    all_bonds_data.append(df)

master_df=pd.concat(all_bonds_data,ignore_index=True)
master_df['value']=pd.to_numeric(master_df['value'])
wide_df=master_df.pivot(index='date',columns='series_id',values='value')
yield_spread_of_10y_2y=wide_df['DGS10']-wide_df['DGS2']
wide_df['yield_spread_of_10y_2y']=yield_spread_of_10y_2y
yield_spread_of_10y_3M=wide_df['DGS10']-wide_df['DGS3MO']
wide_df['yield_spread_of_10y_3M']=yield_spread_of_10y_3M
wide_df=wide_df.dropna()
print(wide_df.tail())
print(wide_df.head())
correlation_matrix=wide_df.corr() #to check correlation between the columns of the dataframe nmaely DGS10, DGS2 and yield_spread
print(correlation_matrix) #The closer a correlation is to -1.0, the stronger the inverse relationship.

csv_file=wide_df.to_csv( index=True) #If we don't use the name, the file will be conveted into one giant text string
                                     # index=True as index is already the date  column as per the pivot
ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
s3=boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)
s3.put_object(Body=csv_file, Bucket='bonds-data-anirudha-4399', Key='multi_series_bonds/Yield_Spread.csv')
print("Upload successful! Check your AWS Console.")

wide_df.index=pd.to_datetime(wide_df.index)

# --- Statistical Visualization ---

#plt.plot(wide_df.index, wide_df['yield_spread_of_10y_2y'].mean(), label='Yield Spread (10Y - 2Y)', color='orange') using mean would simply take the average of the entire row and give a single value, theredoe using rolling average
plt.plot(wide_df.index, wide_df['yield_spread_of_10y_2y'].rolling(window=180).mean(), label='Yield Spread (10Y - 2Y)', color='orange')
# Add the danger line
plt.axhline(y=0, color='red', linestyle='--', label='Inversion Threshold')
plt.title("2-Year Treasury Yield vs. Yield Spread (10Y - 2Y)")
plt.xlabel("Date")
plt.ylabel("Yield Spread (%)")
plt.legend()
plt.show()

#10 Year yield vs 3 month yield spread
plt.plot(wide_df.index, wide_df['yield_spread_of_10y_3M'].rolling(window=180).mean(), label='Yield Spread (10Y - 3M)', color='green')
# Add the danger line
plt.axhline(y=0, color='red', linestyle='--', label='Inversion Threshold')
plt.title("3-Month Treasury Yield vs. Yield Spread (10Y - 3M)")
plt.xlabel("Date")
plt.ylabel("Yield Spread (%)")
plt.legend()
plt.show()

# --- Statistical Visualization (Upgraded) ---
# 1. Make the canvas a bit wider for better readability
plt.figure(figsize=(10, 6))

# 2. Create the Hexbin Density Plot
hb = plt.hexbin(wide_df['DGS2'], wide_df['yield_spread_of_10y_2y'], gridsize=40, cmap='Blues')

# 3. Add a color bar legend to the side
cb = plt.colorbar(hb, label='Number of Days (Density)')

# 4. Add professional labels and a light grid
plt.title("2-Year Treasury Yield vs. Yield Spread Density (10Y - 2Y)")
plt.xlabel("2-Year Yield (%)")
plt.ylabel("Yield Spread (%)")
plt.grid(True, linestyle='--', alpha=0.3)

# 5. Display the canvas
plt.show()

# 3M vs 10Y yield spread density plot
# 1. Make the canvas a bit wider for better readability
plt.figure(figsize=(10, 6))

# 2. Create the Hexbin Density Plot
hb = plt.hexbin(wide_df['DGS3MO'], wide_df['yield_spread_of_10y_3M'], gridsize=40, cmap='Blues')

# 3. Add a color bar legend to the side
cb = plt.colorbar(hb, label='Number of Days (Density)')

# 4. Add professional labels and a light grid
plt.title("3-Month Treasury Yield vs. Yield Spread Density (10Y - 3M)")
plt.xlabel("3-Month Yield (%)")
plt.ylabel("Yield Spread (%)")
plt.grid(True, linestyle='--', alpha=0.3)

# 5. Display the canvas
plt.show()

