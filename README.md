# bond-yield-monitor

#📈 Automated Bond Market Analytics & Macro-Forecasting System

A professional-grade financial data engine designed to monitor the U.S. Treasury Yield Curve and generate real-time Recession Probability Signals. This system automates the extraction of macroeconomic data, computes sophisticated derived metrics, and provides the foundation for predictive machine learning models.

#🎯 Key Analytical Capabilities
Full Curve Monitoring: Real-time tracking of the 3-Month, 2-Year, 5-Year, 10-Year, and 30-Year Treasury yields.

Recession Signal Analytics: Automated calculation of the 2Y-10Y Spread and the 3M-10Y Spread (the Federal Reserve's preferred metric) to identify Yield Curve Inversions.

Inflation Insight: Integrated tracking of 10Y TIPS Breakeven Rates to monitor market-based inflation expectations.

Predictive Intelligence: (In Progress) A Machine Learning pipeline leveraging Random Forest algorithms to forecast spread movements and economic shifts.

#⚙️ System Architecture
Built with production-standard Data Engineering principles:

Extraction: Direct ingestion from the FRED API (St. Louis Fed).

Storage: Automated AWS S3 Data Lake architecture for high-durability historical storage.

Orchestration: Fully serverless execution via GitHub Actions for daily automated updates.

Security: Professional environment variable management to secure cloud credentials.


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



   
