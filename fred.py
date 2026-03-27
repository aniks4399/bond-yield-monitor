import os

import boto3
import pandas as pd
import requests
from dotenv import load_dotenv

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
FRED_SERIES_ID = "DGS10"
CSV_PATH = "bonds_data.csv"
S3_BUCKET = "bonds-data-anirudha-4399"
S3_KEY = "bonds_data_cloud.csv"
REQUEST_TIMEOUT_SECONDS = 30


def get_required_env(*names):
    for name in names:
        value = os.getenv(name)
        if value:
            return value

    joined_names = ", ".join(names)
    raise RuntimeError(f"Missing required environment variable. Set one of: {joined_names}")


def fetch_observations(series_id, api_key):
    response = requests.get(
        FRED_URL,
        params={"series_id": series_id, "api_key": api_key, "file_type": "json"},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    data = response.json()
    observations = data.get("observations")
    if observations is None:
        error_message = data.get("error_message") or "FRED response did not include observations."
        raise RuntimeError(f"FRED API error for {series_id}: {error_message}")

    df = pd.DataFrame(observations)
    if df.empty:
        raise RuntimeError(f"FRED returned no observations for {series_id}.")

    filtered_df = df.loc[df["value"] != ".", ["date", "value"]].copy()
    if filtered_df.empty:
        raise RuntimeError(f"FRED returned observations for {series_id}, but none had usable values.")

    return filtered_df


def get_s3_client():
    access_key = get_required_env("AWS_ACCESS_KEY_ID", "ACCESS_KEY")
    secret_key = get_required_env("AWS_SECRET_ACCESS_KEY", "SECRET_KEY")
    return boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )


def main():
    load_dotenv()

    fred_api_key = get_required_env("FRED_API_KEY")
    bonds_df = fetch_observations(FRED_SERIES_ID, fred_api_key)
    bonds_df.to_csv(CSV_PATH, index=False)

    s3 = get_s3_client()
    s3.upload_file(CSV_PATH, S3_BUCKET, S3_KEY)

    print(bonds_df.tail())
    print("Upload successful! Check your AWS Console.")


if __name__ == "__main__":
    main()
