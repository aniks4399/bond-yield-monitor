import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split  
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.inspection import permutation_importance

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
x=pd.DataFrame(wide_df[['T10Y2Y','T10Y3M','T10Y2Y_5D_diff','DGS3MO','DCOILWTICO','VIXCLS']])  # The corporate bond yield data point is removed to find out which single macro-economic factor contributes towards changes in corporate yields.
y=pd.DataFrame(wide_df[['Target_30D_Corp_Spread']])

#Splitting the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=False)

#Creating and training the model
rf_model = RandomForestRegressor(random_state=42)
rf_model.fit(x_train,y_train.values)
predictions=rf_model.predict(x_test)
mse=mean_squared_error(y_test,predictions)
print(f'Mean Squared Error {mse:.4f}')  

# 1. Run the Scrambler Engine
print("Calculating Feature Importance (Scrambling data...)")
result = permutation_importance(rf_model, x_test, y_test, n_repeats=10, random_state=42)

# 2. Sort the features from least to most important
sorted_idx = result.importances_mean.argsort()

# 3. Build the "Drivers of Panic" Visualization
plt.figure(figsize=(10, 6))
# We use a boxplot to show the variance across the 10 scrambles
plt.boxplot(
    result.importances[sorted_idx].T, 
    vert=False, 
    labels=x_test.columns[sorted_idx]
)
plt.title("What Drives Corporate Credit Spreads? (Permutation Importance)")
plt.xlabel("Drop in Predictive Accuracy (Worse is More Important)")
plt.tight_layout()
plt.show()
