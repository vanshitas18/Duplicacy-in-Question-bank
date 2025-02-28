import streamlit as st
import pandas as pd
import re

def extract_quesans(text):
    match = re.search(r"'question'\s*,\s*'(.+)", str(text))  # Capture everything after 'question'
    return match.group(1).rstrip("')]") if match else None 

# Streamlit UI
st.title("Duplicate Question Analyzer")

uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["csv", "xlsx"])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1]
    if file_extension == "csv":
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # Save corrected version
    corrected_filename = "corrected_" + uploaded_file.name
    df.to_csv(corrected_filename, encoding="utf-8-sig", index=False)
    df = pd.read_csv(corrected_filename)
    
    df["extracted_quesans"] = df["questions"].apply(extract_quesans)
    
    # Count occurrences of each unique question
    duplicate_counts1 = df["extracted_quesans"].value_counts()
    duplicates_only1 = duplicate_counts1[duplicate_counts1 > 1]
    
    # Count occurrences of each unique question within each language
    duplicate_countsgroup1 = df.groupby(["language", "extracted_quesans"]).size().reset_index(name="count")
    
    # Filter only duplicate questions (appear more than once in the same language)
    duplicates_onlygroup1 = duplicate_countsgroup1[duplicate_countsgroup1["count"] > 1]
    
    # Merge back with the original DataFrame to get all matching 'id' values
    duplicates_with_cols1 = df.merge(duplicates_onlygroup1, on=["language", "extracted_quesans"], how="inner")
    
    # Group unique duplicate questions and aggregate IDs as a list
    unq_dup_qa = (
        duplicates_with_cols1.groupby(["language", "extracted_quesans", "count"])["id"]
        .agg(list)
        .reset_index()
    )
    
    # Display results
    st.subheader("Unique Duplicate Questions")
    st.write(unq_dup_qa)
    
    # Provide download option
    csv_file = "unique_duplicate_questions.csv"
    unq_dup_qa.to_csv(csv_file, index=False)
    st.download_button(label="Download CSV", data=open(csv_file, "rb"), file_name=csv_file, mime="text/csv")


#python -m streamlit run st.py