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
