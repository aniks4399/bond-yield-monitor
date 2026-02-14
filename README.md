# bond-yield-monitor

# 📈 Automated Bond Yield Data Pipeline

An end-to-end data engineering project that automates the extraction, transformation, and cloud storage of U.S. Treasury Bond yield data.

## 🛠️ Tech Stack
* **Language:** Python (Pandas, Requests, Boto3)
* **API:** Federal Reserve Economic Data (FRED)
* **Cloud:** AWS S3 (Storage)
* **Automation:** GitHub Actions (CI/CD)
* **Security:** Environment Variables & GitHub Secrets

## ⚙️ How it Works
1. **Extraction:** Python script fetches daily 10-Year Treasury Yield data via the FRED API.
2. **Transformation:** Data is cleaned and formatted into a structured CSV using Pandas.
3. **Storage:** The processed file is automatically uploaded to an AWS S3 bucket.
4. **Orchestration:** A GitHub Actions workflow triggers the script daily at market close.

## 🔐 Cloud Ingestion Layer (AWS S3)

To move beyond local files, this project supports two secure cloud-based ingestion methods for Power BI:

### 🛠️ Connection Methods
1. **Direct Integration (Recommended for Automation):** - Uses the `boto3` library directly inside Power BI's Python connector.
   - Fetches fresh data during every dashboard refresh using environment-stored credentials.
2. **Secure Temporary Access (Utility Script):** - Run `FRED_link_gen.py` to generate a **Presigned URL**.
   - Provides a time-bound (1-hour) link for web-based tools without exposing master keys.

### 💻 Local Development Setup
To run these scripts locally without hardcoding keys:
1. Create a `.env` file in the root directory.
2. Add your credentials:
   ```text
   AWS_ACCESS_KEY_ID=your_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_here
