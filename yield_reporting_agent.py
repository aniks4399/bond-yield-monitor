from google import genai
import datetime
import requests
import pandas as pd
import boto3 
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 1. Initialize your AI Brain with the NEW SDK Client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# 2. Gather Data
def fetch_energy_prices():
    fred_key = os.getenv("FRED_API_KEY")
    series_id_list = ['DCOILWTICO', 'DCOILBRENTEU', 'DHHNGSP']
    all_dataframes = []

    # Calculate dates to only get the last 30 days of data
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)

    for s_id in series_id_list:
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={s_id}&api_key={fred_key}&file_type=json&observation_start={start_date}&observation_end={end_date}"
        
        response = requests.get(url)
        data = response.json()
        
        if 'observations' in data:
            df = pd.DataFrame(data['observations'])
            # Filter out non-numeric holiday/weekend data
            df = df.loc[df['value'] != '.', ['date', 'value']] 
            df['value'] = pd.to_numeric(df['value'])
            df['commodity'] = s_id
            all_dataframes.append(df)

    # Combine all dataframes into one master dataframe
    master_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Pivot the data to make it a clean table for the LLM to read
    pivot_df = master_df.pivot(index='date', columns='commodity', values='value')
    
    # Rename columns for the LLM's understanding
   # Safely rename only the columns that the API successfully returned
    rename_map = {
        'DCOILWTICO': 'WTI Crude',
        'DCOILBRENTEU': 'Brent Crude',
        'DHHNGSP': 'Natural Gas'
    }
    pivot_df = pivot_df.rename(columns=rename_map)
    
    # Let's print out what actually arrived so we can monitor the API's health
    print(f"Data successfully fetched for: {list(pivot_df.columns)}")
    
    return pivot_df

# 3. The Core Agent Logic
def run_research_agent():
    print(f"Agent starting run for week of {datetime.date.today()}...")
    
    prices_df = fetch_energy_prices()
    
    # Convert dataframe to a markdown table string for the LLM
    formatted_data = prices_df.to_markdown()
    
    prompt = f"""
    You are an expert fixed-income and global macroeconomics research assistant.
    Here is the latest daily data for global energy prices over the last 30 days:
    
    {formatted_data}
    
    Please write a brief, professional update suitable for a research article. 
    Focus on how the trend in these specific price movements might impact global inflation 
    expectations and what that could mean for sovereign bond yields.
    """
    
    print("Analyzing data...")
    
    print("Analyzing data...")
    
    # Generate content using the new client syntax
    response = client.models.generate_content(
        model='gemini-3-flash-preview', 
        contents=prompt
    )

    #S3
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    s3=boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    
    # 4. Take Action
    file_name = f"weekly_macro_update_{datetime.date.today()}.md"
    bucket_name = 'bonds-data-anirudha-4399'
    
    print(f"Agent run complete. Article draft saved as {file_name}!")

    s3_key = f"weekly_bond_market_report/weekly_reports/{file_name}"
    # Use put_object and pass Gemini's raw text directly into the 'Body'
    s3.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=response.text
    )
        
    print(f"Agent run complete! Direct upload successful to S3: {s3_key}")

# Run the agent
if __name__ == "__main__":
    run_research_agent()D
