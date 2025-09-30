import streamlit as st
import pandas as pd
import importlib.util
import os
import tempfile

# Set page config
st.set_page_config(
    page_title="TB Data Verification App",
    layout="centered"
)

st.title("🧪 TB Data Verification App")
st.markdown("This tool helps you upload a custom rule file and TB data Excel file for verification.")

# --- Tabs ---
tab1, tab2 = st.tabs(["📜 Upload Rule File", "📊 Upload TB Data File"])

# --- Tab 1: Rule File Upload ---
with tab1:
    st.header("📜 Upload Python Rule File")
    st.markdown("""
    Upload a `.py` file that contains the rule functions to validate your TB data.
    
    The file should define one or more functions to check the data, e.g.:
    ```python
    def check_missing_values(df):
        return df[df['some_column'].isnull()]
    ```
    """)
    
    rule_file = st.file_uploader("Choose a Python (.py) file", type=["py"])

    if rule_file:
        st.success("✅ Rule file uploaded successfully.")
        
        # Save uploaded rule file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp_file:
            tmp_file.write(rule_file.getvalue())
            rule_file_path = tmp_file.name

        # Dynamically import the uploaded rule file
        spec = importlib.util.spec_from_file_location("rules_module", rule_file_path)
        rules_module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(rules_module)
            st.success("✅ Rule file loaded and imported.")
            
            # List functions from rule file
            rule_functions = [func for func in dir(rules_module) if callable(getattr(rules_module, func)) and not func.startswith("__")]
            st.markdown("### 📋 Functions Found in Rule File:")
            st.write(rule_functions)
        except Exception as e:
            st.error(f"❌ Error loading rule file: {e}")

# --- Tab 2: Excel Upload ---
with tab2:
    st.header("📊 Upload TB Excel Data")
    excel_file = st.file_uploader("Choose an Excel file (.xlsx)", type=["xlsx"])

    if excel_file:
        try:
            df = pd.read_excel(excel_file)
            st.success("✅ Excel file uploaded successfully.")
            st.dataframe(df.head())  # Preview first 5 rows
            
            if rule_file:
                st.markdown("---")
                st.markdown("### 🔍 Run Checks Using Uploaded Rules")
                if st.button("Run Rules"):
                    if 'rules_module' in locals():
                        results = {}
                        for func_name in rule_functions:
                            func = getattr(rules_module, func_name)
                            try:
                                result = func(df)
                                results[func_name] = result
                            except Exception as e:
                                results[func_name] = f"❌ Error: {e}"
                        
                        st.markdown("### ✅ Rule Check Results")
                        for rule, result in results.items():
                            st.markdown(f"#### 🔎 {rule}")
                            if isinstance(result, pd.DataFrame):
                                if not result.empty:
                                    st.warning(f"⚠️ Issues found by `{rule}`:")
                                    st.dataframe(result)
                                else:
                                    st.success(f"✅ `{rule}` passed. No issues found.")
                            else:
                                st.error(f"{result}")
                    else:
                        st.warning("Please upload a valid rule file in the first tab.")
            else:
                st.info("Upload a rule file first to enable data checking.")
        except Exception as e:
            st.error(f"❌ Failed to read Excel file: {e}")
