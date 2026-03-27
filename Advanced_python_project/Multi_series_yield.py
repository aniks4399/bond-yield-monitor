import os

import boto3
import matplotlib
import pandas as pd
import requests
from dotenv import load_dotenv

if not os.environ.get("DISPLAY"):
    matplotlib.use("Agg")

import matplotlib.pyplot as plt

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
SERIES_IDS = ["DGS30", "DGS10", "DGS5", "DGS2", "DGS3MO"]
S3_BUCKET = "bonds-data-anirudha-4399"
S3_KEY = "multi_series_bonds/Yield_Spread.csv"
REQUEST_TIMEOUT_SECONDS = 30

def get_required_env(*names):
    for name in names:
        value = os.getenv(name)
        if value:
            return value

    joined_names = ", ".join(names)
    raise RuntimeError(f"Missing required environment variable. Set one of: {joined_names}")


def fetch_series_observations(series_id, api_key):
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

    df = df.loc[df["value"] != ".", ["date", "value"]].copy()
    if df.empty:
        raise RuntimeError(f"FRED returned observations for {series_id}, but none had usable values.")

    df["value"] = pd.to_numeric(df["value"])
    df["series_id"] = series_id
    return df


def get_s3_client():
    access_key = get_required_env("AWS_ACCESS_KEY_ID", "ACCESS_KEY")
    secret_key = get_required_env("AWS_SECRET_ACCESS_KEY", "SECRET_KEY")
    return boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )


def plot_series(wide_df):
    plt.figure(figsize=(10, 6))
    plt.plot(
        wide_df.index,
        wide_df["yield_spread_of_10y_2y"].rolling(window=180).mean(),
        label="Yield Spread (10Y - 2Y)",
        color="orange",
    )
    plt.axhline(y=0, color="red", linestyle="--", label="Inversion Threshold")
    plt.title("2-Year Treasury Yield vs. Yield Spread (10Y - 2Y)")
    plt.xlabel("Date")
    plt.ylabel("Yield Spread (%)")
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(
        wide_df.index,
        wide_df["yield_spread_of_10y_2y"].rolling(window=180).mean(),
        label="Yield Spread (10Y - 2Y)",
        color="orange",
    )
    plt.plot(
        wide_df.index,
        wide_df["DGS2"].rolling(window=180).mean(),
        label="2-Year Treasury Yield",
        color="red",
    )
    plt.axhline(y=0, color="red", linestyle="--", label="Inversion Threshold")
    plt.title("2-Year Treasury Yield vs. Yield Spread (10Y - 2Y)")
    plt.xlabel("Date")
    plt.ylabel("Yield/Spread (%)")
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(
        wide_df.index,
        wide_df["yield_spread_of_10y_3M"].rolling(window=180).mean(),
        label="Yield Spread (10Y - 3M)",
        color="green",
    )
    plt.plot(
        wide_df.index,
        wide_df["DGS3MO"].rolling(window=180).mean(),
        label="3-Month Treasury Yield",
        color="purple",
    )
    plt.axhline(y=0, color="red", linestyle="--", label="Inversion Threshold")
    plt.title("3-Month Treasury Yield vs. Yield Spread (10Y - 3M)")
    plt.xlabel("Date")
    plt.ylabel("Yield Spread (%)")
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()

    plt.figure(figsize=(10, 6))
    hb = plt.hexbin(
        wide_df["DGS2"],
        wide_df["yield_spread_of_10y_2y"],
        gridsize=40,
        cmap="Blues",
    )
    plt.colorbar(hb, label="Number of Days (Density)")
    plt.title("2-Year Treasury Yield vs. Yield Spread Density (10Y - 2Y)")
    plt.xlabel("2-Year Yield (%)")
    plt.ylabel("Yield Spread (%)")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.show()
    plt.close()

    plt.figure(figsize=(10, 6))
    hb = plt.hexbin(
        wide_df["DGS3MO"],
        wide_df["yield_spread_of_10y_3M"],
        gridsize=40,
        cmap="Blues",
    )
    plt.colorbar(hb, label="Number of Days (Density)")
    plt.title("3-Month Treasury Yield vs. Yield Spread Density (10Y - 3M)")
    plt.xlabel("3-Month Yield (%)")
    plt.ylabel("Yield Spread (%)")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.show()
    plt.close()


def main():
    load_dotenv()

    fred_key = get_required_env("FRED_API_KEY")
    all_bonds_data = []

    for maturity_id in SERIES_IDS:
        df = fetch_series_observations(maturity_id, fred_key)
        print(f"Successfully pulled data from {maturity_id}")
        all_bonds_data.append(df)

    master_df = pd.concat(all_bonds_data, ignore_index=True)
    wide_df = master_df.pivot(index="date", columns="series_id", values="value")
    wide_df["yield_spread_of_10y_2y"] = wide_df["DGS10"] - wide_df["DGS2"]
    wide_df["yield_spread_of_10y_3M"] = wide_df["DGS10"] - wide_df["DGS3MO"]
    wide_df = wide_df.dropna()

    print(wide_df.tail())
    print(wide_df.head())
    correlation_matrix = wide_df.corr()
    print(correlation_matrix)

    csv_file = wide_df.to_csv(index=True)
    s3 = get_s3_client()
    s3.put_object(Body=csv_file, Bucket=S3_BUCKET, Key=S3_KEY)
    print("Upload successful! Check your AWS Console.")

    wide_df.index = pd.to_datetime(wide_df.index)
    plot_series(wide_df)


if __name__ == "__main__":
    main()
