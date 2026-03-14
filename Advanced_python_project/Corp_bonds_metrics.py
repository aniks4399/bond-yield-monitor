import requests
import pandas as pd
import matplotlib.pyplot as plt
import boto3
import os
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split  
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

load_dotenv()
fred_key=os.getenv("FRED_API_KEY")
series_ids=['DGS30','DGS10','DGS5','DGS2','DGS3MO','T10Y2Y','T10Y3M','DCOILWTICO','VIXCLS','BAMLC0A0CMEY']
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

#Pulling future yield values of govt and corporate bonds
wide_df['Target_30D_Spread']=wide_df['T10Y2Y'].shift(-30)
wide_df['Target_30D_Corp_Spread']=wide_df['BAMLC0A0CMEY'].shift(-30)

#future_prediction=wide_df.iloc[[-1]][['T10Y2Y','T10Y3M','T10Y2Y_5D_diff','DGS3MO','DCOILWTICO','VIXCLS','BAMLC0A0CMEY']]
#print(future_prediction)

#Removing the rows with missing values
wide_df=wide_df.dropna()

#Creating x and y
x=pd.DataFrame(wide_df[['T10Y2Y','T10Y3M','T10Y2Y_5D_diff','DGS3MO','DCOILWTICO','VIXCLS','BAMLC0A0CMEY']])
y=pd.DataFrame(wide_df[['Target_30D_Spread','Target_30D_Corp_Spread']])

#Splitting the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=False)

#Creating and training the model
rf_model = RandomForestRegressor(random_state=42)
rf_model.fit(x_train,y_train.values)
predictions=rf_model.predict(x_test)
mae=mean_squared_error(y_test,predictions)
print(f'Mean Squared Error: {mae:.4f}')  

# --- KEEP FOR Q2 ROADMAP / COMMENT OUT FOR ARTICLE 6 VISUALS ---
# live_forecast = rf_model.predict(future_prediction)
# print(f"Secret Forecast for Article 6: {live_forecast[0]:.4f}%")


# 1. Visualize the 10Y Spread (Sovereign vs Corporate)
wide_df.index=pd.to_datetime(wide_df.index) # Convert index to datetime for better plotting
plt.figure(figsize=(15,8))
plt.plot(wide_df.index, wide_df['DGS10'].rolling(window=180).mean(), label='10Y US Treasury (Sovereign)', color='blue', alpha=0.7)
plt.plot(wide_df.index, wide_df['BAMLC0A0CMEY'].rolling(window=180).mean(), label='10Y Corp Index (Investment Grade)', color='green', alpha=0.9)

# Fill the gap - this is the "Credit Spread" you mention in your draft
plt.fill_between(wide_df.index, wide_df['DGS10'], wide_df['BAMLC0A0CMEY'], 
                 color='gray', alpha=0.2, label='Credit Spread (Risk Premium)')

plt.title("Visualizing the Risk Premium: Sovereign vs. Corporate (10Y)")
plt.ylabel("Yield (%)")
plt.legend()
plt.show()

# 2. Visualize the 2Y Spread
plt.figure(figsize=(15,8))
plt.plot(wide_df.index, wide_df['DGS2'].rolling(window=180).mean(), label='2Y US Treasury', color='darkblue')
plt.plot(wide_df.index, wide_df['BAMLC0A0CMEY'].rolling(window=180).mean(), label='Corporate Index Proxy', color='darkgreen') # Using the index as proxy
plt.title("2Y Sovereign vs. Corporate Yield Comparison")
plt.ylabel("Yield (%)")
plt.legend()
plt.show()

# 3. Isolating the Credit Spread (The true cost of risk)
wide_df['Credit_Spread'] = wide_df['BAMLC0A0CMEY'] - wide_df['DGS10']

plt.figure(figsize=(15,8))
plt.plot(wide_df.index, wide_df['Credit_Spread'], color='red', label='Corporate Credit Spread (OAS)')
plt.axhline(y=wide_df['Credit_Spread'].mean(), color='black', linestyle='--', label='Historical Average')
plt.title("The 'Fear' Gauge for Corporations: US Corporate Credit Spread")
plt.ylabel("Basis Points / Percentage")
plt.legend()
plt.show()
