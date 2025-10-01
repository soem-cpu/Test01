import streamlit as st
import pandas as pd
from io import BytesIO

# ================================
# APP CONFIG
# ================================
st.set_page_config(
    page_title="TB Data Quality Checker",
    page_icon="🫁",
    layout="wide"
)

# ================================
# HEADER
# ================================
col1, col2 = st.columns([1,4])
with col1:
    st.image("https://www.who.int/images/default-source/departments/tuberculosis/tb-icon.png", width=90)
with col2:
    st.title("🫁 TB Data Quality Checker")
    st.caption("Upload your Excel data, run automated validation checks, and download clean outputs.")

st.markdown("---")

# ================================
# SIDEBAR
# ================================
st.sidebar.header("📂 File Upload")
uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])
st.sidebar.markdown("----")
st.sidebar.image("https://www.cdc.gov/tb/images/tb-prevent.jpg", use_container_width=True)
st.sidebar.markdown("**Tip:** Ensure your Excel has sheets: `Screening`, `Patient data`, `Visit data`, `Service Point`, and `Dropdown`.")

# ================================
# MAIN CONTENT
# ================================
if uploaded_file:
    # Load Excel
    xls = pd.ExcelFile(uploaded_file)
    st.success("✅ File uploaded successfully!")

    # Display sheets as tabs
    tabs = st.tabs(["📋 Screening", "👩‍⚕️ Patient Data", "🏥 Service Point", "📅 Visit Data", "📊 VS_Update"])
    sheet_names = ["Screening", "Patient Data", "Service Point", "Visit Data", "VS_Update"]

    for tab, sheet_name in zip(tabs, sheet_names):
        with tab:
            if sheet_name in xls.sheet_names:
                df = xls.parse(sheet_name)
                st.subheader(f"{sheet_name} Preview")
                st.dataframe(df.head(20), use_container_width=True)
            else:
                st.warning(f"⚠️ `{sheet_name}` sheet not found in uploaded file.")

    st.markdown("---")

    # ================================
    # RUN CHECK BUTTON
    # ================================
    if st.button("🚀 Run Data Quality Checks"):
        from check_rules import check_rules  # your backend
        results = check_rules(uploaded_file, "output.xlsx")
        st.success("✅ Rules applied successfully!")

        # Provide download
        with open("output.xlsx", "rb") as f:
            st.download_button(
                label="📥 Download Cleaned Excel",
                data=f,
                file_name="output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

else:
    st.info("👆 Upload an Excel file from the sidebar to get started.")

# ================================
# FOOTER
# ================================
st.markdown("---")
st.caption("Built for TB program data verification 🫁 | Powered by Streamlit")
