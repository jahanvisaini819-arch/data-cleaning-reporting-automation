import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Data Cleaning & Reporting Automation", page_icon="🧹", layout="wide")
st.title("🧹 Data Cleaning & Reporting Automation")
st.caption("Upload data, clean common quality issues, and generate a downloadable report.")

st.sidebar.header("1. Upload data")
uploaded = st.sidebar.file_uploader("Choose CSV or Excel", type=["csv","xlsx","xls"])
if uploaded:
    try:
        original = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
        source = uploaded.name
    except Exception as exc:
        st.error(f"Could not read file: {exc}")
        st.stop()
else:
    original = pd.read_csv("messy_sales_data.csv")
    source = "Fictional sample dataset"
    st.sidebar.info("Using included fictional sample data.")

st.sidebar.header("2. Cleaning options")
remove_duplicates = st.sidebar.checkbox("Remove duplicate rows", True)
trim_text = st.sidebar.checkbox("Trim extra spaces", True)
normalize_text = st.sidebar.checkbox("Standardize text case (Title Case)", True)
numeric_rule = st.sidebar.selectbox("Fill missing numeric values", ["Median","Mean","Zero","Leave missing"])
text_rule = st.sidebar.selectbox("Fill missing text values", ["Mode (most common)","Unknown","Leave missing"])

if original.empty:
    st.warning("The dataset has no rows.")
    st.stop()

cleaned = original.copy()
rows_before = len(cleaned)
missing_before = int(cleaned.isna().sum().sum())
duplicates_before = int(cleaned.duplicated().sum())

if trim_text or normalize_text:
    for col in cleaned.select_dtypes(include=["object","string"]).columns:
        values = cleaned[col].astype("string")
        if trim_text:
            values = values.str.strip()
        if normalize_text:
            values = values.str.lower().str.title()
        cleaned[col] = values

if remove_duplicates:
    cleaned = cleaned.drop_duplicates().copy()

for col in cleaned.columns:
    if pd.api.types.is_numeric_dtype(cleaned[col]):
        if numeric_rule == "Median" and cleaned[col].notna().any():
            cleaned[col] = cleaned[col].fillna(cleaned[col].median())
        elif numeric_rule == "Mean" and cleaned[col].notna().any():
            cleaned[col] = cleaned[col].fillna(cleaned[col].mean())
        elif numeric_rule == "Zero":
            cleaned[col] = cleaned[col].fillna(0)
    else:
        if text_rule == "Mode (most common)" and cleaned[col].notna().any():
            mode = cleaned[col].mode(dropna=True)
            if not mode.empty:
                cleaned[col] = cleaned[col].fillna(mode.iloc[0])
        elif text_rule == "Unknown":
            cleaned[col] = cleaned[col].fillna("Unknown")

rows_after = len(cleaned)
missing_after = int(cleaned.isna().sum().sum())
duplicates_after = int(cleaned.duplicated().sum())

st.info(f"Data source: {source}. Review cleaning choices before using the output.")
a,b,c,d = st.columns(4)
a.metric("Original rows", f"{rows_before:,}")
b.metric("Cleaned rows", f"{rows_after:,}")
c.metric("Missing values", f"{missing_before:,}", delta=f"{missing_after-missing_before:+,}")
d.metric("Duplicate rows", f"{duplicates_before:,}", delta=f"{duplicates_after-duplicates_before:+,}")

tab1,tab2,tab3 = st.tabs(["Original Data","Quality Report","Cleaned Data"])
with tab1:
    st.dataframe(original.head(100), use_container_width=True)
with tab2:
    miss = pd.DataFrame({"Column":original.columns,
        "Before cleaning":[int(original[col].isna().sum()) for col in original.columns],
        "After cleaning":[int(cleaned[col].isna().sum()) for col in cleaned.columns]})
    miss_long = miss.melt(id_vars="Column",var_name="Stage",value_name="Missing values")
    st.plotly_chart(px.bar(miss_long,x="Column",y="Missing values",color="Stage",barmode="group"),use_container_width=True)
    summary = pd.DataFrame({"Metric":["Rows before","Rows after","Duplicate rows found","Duplicate rows remaining","Missing values before","Missing values after"],
        "Value":[rows_before,rows_after,duplicates_before,duplicates_after,missing_before,missing_after]})
    profile = pd.DataFrame({"Column":original.columns,"Data type":[str(original[c].dtype) for c in original.columns],
        "Missing":[int(original[c].isna().sum()) for c in original.columns],"Unique values":[int(original[c].nunique(dropna=True)) for c in original.columns]})
    st.subheader("Cleaning summary")
    st.dataframe(summary,use_container_width=True,hide_index=True)
    st.subheader("Column profile")
    st.dataframe(profile,use_container_width=True,hide_index=True)
with tab3:
    st.dataframe(cleaned.head(500),use_container_width=True)

def excel_report():
    from io import BytesIO
    buf = BytesIO()
    with pd.ExcelWriter(buf,engine="openpyxl") as writer:
        cleaned.to_excel(writer,index=False,sheet_name="Cleaned_Data")
        miss.to_excel(writer,index=False,sheet_name="Missing_Values")
        summary.to_excel(writer,index=False,sheet_name="Cleaning_Summary")
        profile.to_excel(writer,index=False,sheet_name="Data_Profile")
    return buf.getvalue()

st.divider()
x,y = st.columns(2)
x.download_button("Download cleaned CSV",cleaned.to_csv(index=False).encode("utf-8"),"cleaned_data.csv","text/csv",use_container_width=True)
y.download_button("Download Excel report",excel_report(),"automated_cleaning_report.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
st.caption("Sample data is fictional. Review automated cleaning choices before using cleaned values for real business decisions.")
