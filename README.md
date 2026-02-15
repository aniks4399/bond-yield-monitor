# bond-yield-monitor

# 📈 Bond Yield Monitoring Pipeline

A professional end-to-end data engineering pipeline that automates the collection, storage, and visualization of 10-Year Treasury Yield data.

## 🚀 Architecture Overview
- **Data Source:** FRED (Federal Reserve Economic Data) API.
- **Storage:** Amazon S3 (AWS Data Lake).
- **Orchestration:** GitHub Actions (Daily automated runs).
- **Visualization:** Power BI Desktop with Direct S3 Integration.

---

## 📂 Project Structure
- `fred.py`: The core ingestion engine. Extracts data from FRED and uploads it to S3.
- `powerbi_connector.py`: 🆕 The script used inside Power BI to fetch data directly from S3.
- `FRED_LINK_GEN.py`: Utility tool for generating secure, time-bound "Presigned URLs" (1-hour access).
- `.gitignore`: Ensures local credentials in `.env` are never pushed to GitHub.

---

## 🔐 Cloud Ingestion Layer (AWS S3)
This project supports two distinct ways to connect S3 data to Power BI:

### 1. Automated Integration (Main Dashboard)
Uses the `boto3` library directly within Power BI's Python connector. This ensures the dashboard stays up-to-date with every refresh without manual intervention.

### 2. Secure Temporary Access (Utility)
Run `FRED_LINK_GEN.py` to create a **Presigned URL**. This is ideal for sharing data with external stakeholders who don't have AWS access, providing them a secure "VIP link" that expires after 60 minutes.

---

## 🛠️ Local Setup
1. Clone the repository.
2. Create a `.env` file in the root directory:
   ```text
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
