import streamlit as st
import pandas as pd
import importlib.util
import io

# Configuration
st.set_page_config(page_title="Dynamic Rule-Based Data Verification", layout="wide")

# Custom CSS for improved aesthetics
st.markdown(
    """
    <style>
    .big-font {
        font-size:24px !important;
        font-weight: bold;
    }
    .reportview-container {
        background: #f0f2f6;
    }
    .stButton>button {
        color: #4F8BF9;
        border: 2px solid #4F8BF9;
        background-color: #ffffff;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #4F8BF9;
        color: white;
    }
    .stTextInput>label, .stFileUploader>label {
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# App Title and Introduction
st.title("📊 Dynamic Rule-Based Data Verification App")
st.markdown(
    """
    <p class='big-font'>
        Upload your <strong>Python rules file</strong> and the <strong>Excel/CSV file</strong> you want to verify.
        The app dynamically applies the rules and shows validation results.
        You can download all results as a multi-sheet Excel file.
    </p>
    """,
    unsafe_allow_html=True,
)

# File Upload Section
st.sidebar.header("File Uploads")
rules_file = st.sidebar.file_uploader(
    "Upload Python rules file (.py)", type=["py"], help="Upload a .py file containing your validation rules."
)
data_file = st.sidebar.file_uploader(
    "Upload Excel/CSV file to verify", type=["xlsx", "csv"], help="Upload the data file to be validated."
)

# Function to load rules
def load_rules(rules_file):
    with open("rules_temp.py", "wb") as f:
        f.write(rules_file.getbuffer())
    spec = importlib.util.spec_from_file_location("rules_module", "rules_temp.py")
    rules_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rules_module)
    st.success("✅ Rules file loaded!", icon="✅")
    return rules_module

# Main Logic
if rules_file and data_file:
    # Load the rules module
    rules_module = load_rules(rules_file)

    # Data Preview Section
    st.header("Data Preview")
    try:
        if data_file.name.endswith("xlsx"):
            xls = pd.ExcelFile(data_file)
            preview_sheet = xls.sheet_names[0]
            df_preview = xls.parse(preview_sheet)
            st.info(f"Preview of uploaded data (first sheet: {preview_sheet}):")
            st.dataframe(df_preview.head())
        else:
            df_preview = pd.read_csv(data_file)
            st.info("Preview of uploaded data:")
            st.dataframe(df_preview.head())
    except Exception as e:
        st.error(f"Error previewing data: {e}")

    # Apply Rules and Prepare Download
    try:
        results = rules_module.check_rules(data_file)
        excel_output = io.BytesIO()
        sheet_count = 0

        # Prepare multi-sheet Excel file
        with pd.ExcelWriter(excel_output, engine='xlsxwriter') as writer:
            if isinstance(results, dict):
                st.header("Validation Results:")
                for k, v in results.items():
                    st.subheader(k)
                    if isinstance(v, pd.DataFrame):
                        if not v.empty:
                            st.dataframe(v)
                        else:
                            st.success(f"✅ No issues found in {k}!")
                        v.to_excel(writer, index=False, sheet_name=k[:31])
                        sheet_count += 1
                    else:
                        st.write(v)
            elif isinstance(results, pd.DataFrame):
                if results.empty:
                    st.success("✅ No validation issues found!")
                else:
                    st.header("Validation Results:")
                    st.dataframe(results)
                results.to_excel(writer, index=False, sheet_name="Validation")
                sheet_count += 1
            else:
                st.write(results)

        if sheet_count > 0:
            st.download_button(
                label="Download ALL Results as Excel (multi-sheet)",
                data=excel_output.getvalue(),
                file_name="all_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
    except Exception as e:
        st.error(f"Error running rules: {e}")

# Footer
st.markdown("---")
st.markdown("Created with Streamlit")
