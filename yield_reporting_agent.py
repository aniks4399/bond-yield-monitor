from google import genai
import datetime
import requests
import pandas as pd
import os
import time
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
    
    # Browser headers to bypass the cloud runner block
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for s_id in series_id_list:
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={s_id}&api_key={fred_key}&file_type=json&observation_start={start_date}&observation_end={end_date}"
        
        # 3-attempt retry loop
        for attempt in range(3):
            try:
                print(f"Attempt {attempt + 1}: Fetching data for {s_id}...")
                response = requests.get(url, headers=headers)
                response.raise_for_status() 
                
                data = response.json()
                
                if 'observations' in data:
                    df = pd.DataFrame(data['observations'])
                    df = df.loc[df['value'] != '.', ['date', 'value']] 
                    df['value'] = pd.to_numeric(df['value'])
                    df['commodity'] = s_id
                    all_dataframes.append(df)
                    
                print(f"Successfully pulled data for {s_id}!")
                break 
                
            except (requests.exceptions.RequestException, ValueError) as e:
                print(f"Warning: {s_id} attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    print("Waiting 5 seconds before retrying...")
                    time.sleep(5)
                else:
                    print(f"Error: All retry attempts exhausted for {s_id}")
                    raise e

    # Combine and pivot
    master_df = pd.concat(all_dataframes, ignore_index=True)
    pivot_df = master_df.pivot(index='date', columns='commodity', values='value')
    
    rename_map = {
        'DCOILWTICO': 'WTI Crude',
        'DCOILBRENTEU': 'Brent Crude',
        'DHHNGSP': 'Natural Gas'
    }
    pivot_df = pivot_df.rename(columns=rename_map)
    
    print(f"Data successfully fetched for: {list(pivot_df.columns)}")
    return pivot_df

# 3. The Core Agent Logic
def run_research_agent():
    print(f"Agent starting run for week of {datetime.date.today()}...")
    
    prices_df = fetch_energy_prices()
    formatted_data = prices_df.to_markdown()
    
    prompt = f"""
    You are an expert fixed-income and global macroeconomics research assistant.
    Here is the latest daily data for global energy prices over the last 30 days:
    
    {formatted_data}
    
    Please write a brief, professional update suitable for a research article. 
    Focus on how the trend in these specific price movements might impact global inflation 
    expectations and what that could mean for sovereign bond yields.

    Build a model for pedicting yields and yield spreads based on the energy price data and 
    include a simple analysis of the correlation between them.
    """
    
    print("Analyzing data...")
    
    # Generate content
    response = client.models.generate_content(
        model='gemini-3-flash-preview', 
        contents=prompt
    )

    # 4. Save to Local File (Instead of S3)
    file_name = f"weekly_macro_update_{datetime.date.today()}.md"
    
    # Open the file in write mode and save the LLM's text
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(response.text)
        
    print(f"Agent run complete! Article draft saved locally as: {file_name}")

if __name__ == "__main__":
    run_research_agent()