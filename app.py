import streamlit as st
import pandas as pd
import importlib.util
import os

# Title of the app
st.title("Tuberculosis Data Analysis App")

# Image URL
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Pulmonary_tuberculosis_01.jpg/640px-Pulmonary_tuberculosis_01.jpg"
st.image(image_url, caption="Understanding Tuberculosis Data")

# File uploaders
rule_file = st.file_uploader("Upload Rule File (.py)", type=["py"])
excel_file = st.file_uploader("Upload Excel File (.xlsx, .xls)", type=["xlsx", "xls"])

# Sidebar for additional options
with st.sidebar:
    st.header("Analysis Options")
    filter_data = st.checkbox("Apply Data Filter")
    analysis_type = st.selectbox("Choose Analysis Type", ["Descriptive", "Predictive"])

# Main area for displaying results
st.header("Data and Results")

# Function to load rules from the .py file
def load_rules(file_path):
    spec = importlib.util.spec_from_file_location("rule_module", file_path)
    rule_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rule_module)
    return rule_module

if rule_file is not None:
    st.subheader("Rule File Content")
    
    # Save the uploaded file to a temporary location
    with open("temp_rule_file.py", "wb") as f:
        f.write(rule_file.read())
    
    # Load the rules from the .py file
    rule_module = load_rules("temp_rule_file.py")
    
    st.write("Rules loaded successfully!")

if excel_file is not None:
    st.subheader("Excel Data")
    df = pd.read_excel(excel_file)
    st.dataframe(df)

    if rule_module is not None:
        try:
            # Assuming the rule file has a function to specify the column name
            column_name = rule_module.get_column_name()
            
            if filter_data:
                st.subheader("Filtered Data")
                filtered_df = df[df[column_name] > 10]  # Use the column name from the rule file
                st.dataframe(filtered_df)

            st.subheader("Analysis Type")
            st.write(f"Selected analysis type: {analysis_type}")

            # Apply rules based on the loaded module
            if hasattr(rule_module, 'apply_rules'):
                processed_data = rule_module.apply_rules(df)  # Apply rules to the data
                st.subheader("Processed Data with Rules")
                st.dataframe(processed_data)
            else:
                st.error("Error: The rule file must contain a function called 'apply_rules'.")
            
        except AttributeError:
            st.error("Error: The rule file must contain a function called 'get_column_name'.")
        except KeyError as e:
            st.error(f"Error: The column '{column_name}' specified in the rule file does not exist in the Excel data.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Clean up temporary file
if os.path.exists("temp_rule_file.py"):
    os.remove("temp_rule_file.py")

# Footer
st.markdown("---")
st.write("Developed by [Your Name]")
