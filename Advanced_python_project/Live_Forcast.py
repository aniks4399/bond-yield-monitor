import requests
import pandas as pd
import matplotlib.pyplot as plt
import boto3
import os
from dotenv import load_dotenv
import sqlite3
from sklearn.model_selection import train_test_split  
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

load_dotenv()
fred_key=os.getenv("FRED_API_KEY")
series_ids=['DGS30','DGS10','DGS5','DGS2','DGS3MO','T10Y2Y','T10Y3M','DCOILWTICO','VIXCLS']
all_bonds_data=[]
for maturity_id in series_ids:

    url=f"https://api.stlouisfed.org/fred/series/observations?series_id={maturity_id}&api_key={fred_key}&file_type=json"
    response=requests.get(url)
    data=response.json()
    df=pd.DataFrame(data['observations'])
    df=df.loc[df['value']!='.',['date','value']]
    df['series_id']=maturity_id
    all_bonds_data.append(df)

# Combine all the data into a single DataFrame
master_df=pd.concat(all_bonds_data,ignore_index=True)
master_df['value']=pd.to_numeric(master_df['value'])

# Pivot the DataFrame to have dates as index and series_ids as columns
wide_df=master_df.pivot(index='date',columns='series_id',values='value')

#5 DAY Spread
wide_df['T10Y2Y_5D_diff']=wide_df['T10Y2Y'].diff(periods=5)

#removing NAn values
wide_df=wide_df.ffill() #forward fill to replace NaN values with the last valid observation

#Pulling future yield values
wide_df['Target_30D_Spread']=wide_df['T10Y2Y'].shift(-30)

#print(wide_df.tail(2))
#print(wide_df.head(2))
future_prediction=wide_df.iloc[[-1]][['T10Y2Y','T10Y3M','T10Y2Y_5D_diff','DGS3MO','DCOILWTICO','VIXCLS']]
print(future_prediction)
#Removing the rows with missing values
wide_df=wide_df.dropna()

# Print the first and last few rows of the DataFrame to verify the data
#print(wide_df.tail(2))
#print(wide_df.head(2))

#Creating x and y
x=pd.DataFrame(wide_df[['T10Y2Y','T10Y3M','T10Y2Y_5D_diff','DGS3MO','DCOILWTICO','VIXCLS']])
y=pd.DataFrame(wide_df['Target_30D_Spread'])

#Splitting the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=False)

#Creating and training the model
rf_model = RandomForestRegressor(random_state=42)
rf_model.fit(x_train,y_train.values.ravel())
live_forcast=rf_model.predict(future_prediction)
print(f"Predicted 30 day spread from today: {live_forcast[0]:.4f}")
