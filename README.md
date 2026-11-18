# Data Cleaning & Reporting Automation

Streamlit app to upload CSV/Excel data, remove exact duplicate rows, trim and standardize text, handle missing values, inspect data quality, and export cleaned data and a multi-sheet Excel report.

## Files
- `app.py` — interactive dashboard
- `messy_sales_data.csv` and `.xlsx` — fictional sample data with missing values, duplicate rows, inconsistent casing/spaces, and a malformed date field
- `requirements.txt` — dependencies

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Upload all files to a GitHub repository. Open https://share.streamlit.io/, sign in with GitHub, create an app, select your repository and branch, set main file path to `app.py`, and deploy.

## Use your own data
Upload CSV or Excel. The app is designed for general tabular data. Review the selected cleaning rules before using results.
The bundled sample data is fictional and intended for demonstration only.
