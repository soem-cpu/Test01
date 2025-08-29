import streamlit as st
import pandas as pd

st.title("✅ Rule-based Data Verification App")

uploaded_file = st.file_uploader("Upload Excel/CSV file", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("### Preview of your Data", df.head())

    # Example rule: Flag rows where "Age" is missing
    if "Age" in df.columns:
        df["Age_missing"] = df["Age"].isna()

    st.write("### Cleaned Data", df.head())
