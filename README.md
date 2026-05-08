# bond-yield-monitor

📈 **Automated Bond Market Analytics, Macro-Forecasting & AI Reporting System**

A professional-grade financial data engine designed to monitor the U.S. Treasury Yield Curve, generate real-time Recession Probability Signals, and autonomously write macroeconomic research reports. This system automates the extraction of macroeconomic data, computes sophisticated derived metrics, provides the foundation for predictive machine learning models, and leverages Generative AI for market synthesis.

## 🎯 Key Analytical Capabilities

* **Full Curve Monitoring:** Real-time tracking of the 3-Month, 2-Year, 5-Year, 10-Year, and 30-Year Treasury yields.
* **Recession Signal Analytics:** Automated calculation of the 2Y-10Y Spread and the 3M-10Y Spread (the Federal Reserve's preferred metric) to identify Yield Curve Inversions. 
* **Yield Spread Prediction:** Prediction of next 30 days yield spread for T10Y2Y and Corporate Bonds.
* **Autonomous Macro Research (NEW):** An integrated AI agent that analyzes rolling 30-day global energy prices (WTI, Brent, Natural Gas) to generate professional, Substack-ready markdown reports on inflation expectations and sovereign debt impacts.

## 🚀 Multi-Target Macro-Financial Forecasting Engine 

An automated Python pipeline that integrates **Sovereign Bond Yields**, **Corporate Credit Spreads**, and **Exogenous Macro Shocks** (Energy & Volatility) to simulate and forecast yield curve dynamics.

### Key Features
* **Multi-Target Machine Learning:** Simultaneously forecasts Treasury Yield Spreads and Corporate Borrowing Costs using Random Forest Regressors. Also predicts which macro-economic factor contributes to higher or lower yields for corporate bonds.
* **Macro-Aware Feature Engineering:** Incorporates WTI Crude Oil (Energy Shocks) and VIX (Market Fear) to increase model robustness against geopolitical events.
* **Production ETL:** Live data ingestion from FRED APIs with automated data cleaning, forward-filling for lags, and data leakage prevention.
* **Generative AI Agent:** Streams data-driven analytical drafts directly to AWS S3 without local disk I/O, utilizing Google's Gemini LLM.
* **Decoupled Cloud Orchestration:** Microservice architecture using separate GitHub Actions workflows to isolate daily data gathering from periodic AI reporting.

## 🛠️ Tech Stack

* **Languages & Libraries:** Python (Pandas, Scikit-Learn, Requests, Google GenAI SDK, Matplotlib)
* **Infrastructure:** AWS S3 (Data Lake), GitHub Actions (CI/CD Orchestration), Boto3
* **AI/LLM:** Google Gemini API 

## ⚙️ System Architecture

Built with production-standard Data Engineering principles:

* **Extraction:** Direct ingestion from the FRED API (St. Louis Fed).
* **Storage:** Automated AWS S3 Data Lake architecture for high-durability historical storage.
* **Orchestration:** Fully serverless execution via GitHub Actions.
* **Analysis:** Cloud-native generation of markdown reports via LLM.
* **Security:** Professional environment variable management to secure cloud credentials.

### Architecture Overview
* **Data Source:** FRED (Federal Reserve Economic Data) API.
* **Storage:** Amazon S3 (AWS Data Lake).
* **Orchestration:** GitHub Actions (Decoupled Daily ETL & Monthly AI runs).
* **Visualization:** Power BI Desktop with Direct S3 Integration.

## 📂 Project Structure

* `fred.py`: The core ingestion engine. Extracts the 10-Year yield from FRED and uploads it to S3.
* `Advanced_python_project/Multi_series_yield.py`: Advanced math pipeline calculating 3M-10Y and 2Y-10Y spreads and saving multi-series data to S3.
* `yield_reporting_agent.py`: Autonomous Gemini AI agent that fetches 30-day energy shocks and streams markdown macroeconomic reports directly to S3.
* `.github/workflows/`: Contains `daily_bond_yield_tracker.yml` and `agentic_yield_reporter.yml` for isolated cloud execution.
* `powerbi_connector.py`: 🆕 The script used inside Power BI to fetch data directly from S3.
* `FRED_LINK_GEN.py`: Utility tool for generating secure, time-bound "Presigned URLs" (1-hour access).
* `.gitignore`: Ensures local credentials in `.env` are never pushed to GitHub.

## 🔐 Cloud Ingestion Layer (AWS S3)

This project supports two distinct ways to connect S3 data to Power BI:

### 1. Automated Integration (Main Dashboard)
Uses the `boto3` library directly within Power BI's Python connector. This ensures the dashboard stays up-to-date with every refresh without manual intervention.

### 2. Secure Temporary Access (Utility)
Run `FRED_LINK_GEN.py` to create a **Presigned URL**. This is ideal for sharing data with external stakeholders who don't have AWS access, providing them a secure "VIP link" that expires after 60 minutes.

## 🔧 Local Setup

1. Clone the repository.
2. Create a `.env` file in the root directory with the following structure:

```text
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
FRED_API_KEY=your_fred_api_key
GOOGLE_API_KEY=your_gemini_api_key
