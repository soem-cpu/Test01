import streamlit as st
import pandas as pd
import io
import importlib.util

# Configuration
st.set_page_config(page_title="Dynamic Rule-Based Data Verification", layout="wide")

# Custom Theme
primary_color = "#2E9AFE"
secondary_color = "#D1F2EB"
text_color = "#2E4053"
background_color = "#F5F5F5"

st.markdown(
    f"""
    <style>
    body {{
        color: {text_color};
        background-color: {background_color};
    }}
    .big-font {{
        font-size:24px !important;
        font-weight: bold;
    }}
    .reportview-container .main .stButton>button {{
        color: white;
        border: 2px solid {primary_color};
        background-color: {primary_color};
        transition: all 0.3s ease;
    }}
    .reportview-container .main .stButton>button:hover {{
        background-color: {secondary_color};
        color: {text_color};
    }}
    .stTextInput>label, .stFileUploader>label {{
        font-weight: bold;
        color: {text_color};
    }}
    .dataframe th {{
        background-color: {primary_color} !important;
        color: white !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and Introduction with Custom Colors
st.title(f"📊 Dynamic Rule-Based Data Verification App")
st.markdown(
    f"""
    <p class='big-font'>
        Upload your <strong>Python rules file</strong> and the <strong>Excel/CSV file</strong> you want to verify.
        The app dynamically applies the rules and shows validation results.
        Download results as a multi-sheet Excel file.
    </p>
    """,
    unsafe_allow_html=True,
)

# Default rules.py content
default_rules_code = """
import pandas as pd

def check_rules(df):
    '''Check the given DataFrame against a set of rules.'''
    
    # Example rule: Check if 'column1' exists
    if 'column1' not in df.columns:
        return "Error: 'column1' not found"
    
    # Example rule: Check if 'column2' has any missing values
    if df['column2'].isnull().any():
        return "Error: 'column2' has missing values"
    
    # Example: Create a DataFrame with rows that failed validation
    failed_rows = df[df['column3'] < 0]
    
    # If there are failed rows, return them in a dict, else return the whole df
    if not failed_rows.empty:
        return {'Failed Validation': failed_rows}
    else:
        return df
"""

# File Upload Section
st.sidebar.header("File Uploads")
with st.sidebar.expander("Upload Files"):
    rules_file = st.file_uploader(
        "Python Rules File (.py)", type=["py"], help="Upload a .py file containing your validation rules."
    )
    data_file = st.file_uploader(
        "Excel/CSV File to Verify", type=["xlsx", "csv"], help="Upload the data file to be validated."
    )

# Load rules
def load_rules(rules_file):
    if rules_file:
        with st.spinner("Loading rules..."):
            try:
                with open("rules_temp.py", "wb") as f:
                    f.write(rules_file.getbuffer())
                spec = importlib.util.spec_from_file_location("rules_module", "rules_temp.py")
                rules_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(rules_module)
                st.success("✅ Custom rules loaded!", icon="✅")
                return rules_module
            except Exception as e:
                st.error(f"Error loading custom rules: {e}")
                return None
    else:
        with st.spinner("Loading default rules..."):
            try:
                rules_namespace = {}
                exec(default_rules_code, rules_namespace)
                st.info("ℹ️ Using default rules.", icon="ℹ️")
                return type('DefaultRules', (object,), rules_namespace)
            except Exception as e:
                st.error(f"Error loading default rules: {e}")
                return None

# Main Logic
if data_file:
    # Load the rules module
    rules_module = load_rules(rules_file)

    # Determine file type and read data
    if data_file.name.endswith("xlsx"):
        xls = pd.ExcelFile(data_file)
        sheet_names = xls.sheet_names
        selected_sheet = st.selectbox("Select a sheet from the Excel file:", sheet_names)
        df = xls.parse(selected_sheet)
    else:
        df = pd.read_csv(data_file)

    # Data Preview Section
    st.header("Data Preview")
    try:
        st.info("Preview of uploaded data:")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Error previewing data: {e}")

    # Apply Rules and Prepare Download
    if rules_module:
        try:
            check_rules = rules_module.check_rules if hasattr(rules_module, "check_rules") else rules_module.check_rules

            results = check_rules(df)
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
    else:
        st.warning("No rules loaded. Please upload a rules file.")

# Footer
st.markdown("---")
st.markdown("Created with Streamlit")
