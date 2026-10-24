import streamlit as st
import pandas as pd
import time


#  APP CONFIGURATION

st.set_page_config(
    page_title="Wesley's Data Prep Suite",
    layout="wide"
)


#  APP TITLE

st.title(" Wesley's Data Prep Suite")
st.write(
    "Upload your CSV or Excel dataset and clean it automatically or manually."
)


#  FILE UPLOAD

uploaded_file = st.file_uploader(
    "Upload your dataset",
    type=["csv", "xlsx"]
)


#  PROCESS FILE

if uploaded_file:

    
    #  FILE INFO
    
    st.info(f" File Name: {uploaded_file.name}")
    st.info(f" File Type: {uploaded_file.type}")

    
    #  READ FILE SAFELY
    
    try:

        if uploaded_file.name.endswith(".csv"):

            df = pd.read_csv(
                uploaded_file,
                encoding="latin1",
                on_bad_lines="skip",
                sep=None,
                engine="python"
            )

        elif uploaded_file.name.endswith(".xlsx"):

            df = pd.read_excel(uploaded_file)

        else:
            st.error(" Unsupported file format.")
            st.stop()

    except Exception as e:
        st.error(f" Error loading file: {e}")
        st.stop()

    
    #  STORE ORIGINAL DATA
    
    original_df = df.copy()

    
    #  ORIGINAL DATA PREVIEW
    
    st.subheader(" Original Dataset")
    st.dataframe(original_df)

    
    #  INITIAL DATA STATS
    
    initial_rows = df.shape[0]
    initial_cols = df.shape[1]
    initial_missing = df.isnull().sum().sum()
    initial_duplicates = df.duplicated().sum()

    
    #  AUTO CLEAN SECTION
    
    st.subheader(" Auto Clean Data")

    auto_clean = st.button("Run Auto Clean")

    
    #  START TIMER
    
    start_time = time.time()

    records_removed = 0

    
    #  AUTO CLEANING PROCESS
    
    if auto_clean:

        
        # Remove duplicates
        
        before_duplicates = df.shape[0]

        df = df.drop_duplicates()

        after_duplicates = df.shape[0]

        records_removed += (before_duplicates - after_duplicates)

        
        # Remove fully empty columns
      
        df = df.dropna(axis=1, how="all")

        
        # Numeric columns
        
        numeric_cols = df.select_dtypes(include=["number"]).columns

        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].median())

        
        # Text columns
        
        categorical_cols = df.select_dtypes(include=["object"]).columns

        for col in categorical_cols:

            # Fill missing with mode
            if not df[col].mode().empty:
                df[col] = df[col].fillna(df[col].mode()[0])

            # Clean text
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.lower()
            )

        st.success("✅ Auto cleaning completed successfully!")

    
    #  MANUAL CLEANING OPTIONS
    
    st.subheader(" Manual Cleaning Options")

    remove_duplicates = st.checkbox("Remove duplicates")
    drop_missing = st.checkbox("Drop rows with missing values")
    fill_missing_zero = st.checkbox("Fill missing values with 0")
    lowercase_text = st.checkbox("Convert text to lowercase")
    strip_spaces = st.checkbox("Trim text spaces")

    drop_columns = st.multiselect(
        "Drop columns",
        df.columns
    )

    
    #  APPLY MANUAL CLEANING
   
    if remove_duplicates:

        before_manual = df.shape[0]

        df = df.drop_duplicates()

        after_manual = df.shape[0]

        records_removed += (before_manual - after_manual)

    if drop_missing:

        before_missing = df.shape[0]

        df = df.dropna()

        after_missing = df.shape[0]

        records_removed += (before_missing - after_missing)

    if fill_missing_zero:
        df = df.fillna(0)

    if strip_spaces:

        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].astype(str).str.strip()

    if lowercase_text:

        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].astype(str).str.lower()

    if drop_columns:
        df = df.drop(columns=drop_columns)

    
    #  END TIMER
   
    end_time = time.time()

    cleaning_time = round(end_time - start_time, 2)

    
    #  FINAL STATS
   
    final_rows = df.shape[0]
    final_cols = df.shape[1]
    final_missing = df.isnull().sum().sum()
    final_duplicates = df.duplicated().sum()

    
    #  CLEANED DATA
   
    st.subheader(" Cleaned Dataset")
    st.dataframe(df)

   
    #  DATA QUALITY REPORT
    
    st.subheader(" Data Quality Report")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Rows Before", initial_rows)
        st.metric("Rows After", final_rows)

    with col2:
        st.metric("Columns Before", initial_cols)
        st.metric("Columns After", final_cols)

    with col3:
        st.metric("Missing Before", initial_missing)
        st.metric("Missing After", final_missing)

    with col4:
        st.metric("Duplicates Before", initial_duplicates)
        st.metric("Duplicates After", final_duplicates)

    
    #  CLEANING PERFORMANCE
   
    st.subheader(" Cleaning Performance")

    perf1, perf2, perf3 = st.columns(3)

    with perf1:
        st.metric("Total Records", final_rows)

    with perf2:
        st.metric("Records Removed", records_removed)

    with perf3:
        st.metric("Cleaning Time (Seconds)", cleaning_time)

    st.success(
        f"✅ Dataset cleaned successfully in {cleaning_time} seconds!"
    )

    
    # MISSING VALUES REPORT
    
    st.subheader("Missing Values Per Column (Before Cleaning)")

    missing_before = (
        original_df.isnull()
        .sum()
        .reset_index()
    )

    missing_before.columns = ["Column", "Missing Values"]

    st.dataframe(missing_before)

    st.subheader(" Missing Values Per Column (After Cleaning)")

    missing_after = (
        df.isnull()
        .sum()
        .reset_index()
    )

    missing_after.columns = ["Column", "Missing Values"]

    st.dataframe(missing_after)

    
    # DATA TYPES REPORT
    
    st.subheader("Data Types")

    dtype_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str)
    })

    st.dataframe(dtype_df)

    
    #  DOWNLOAD CLEANED DATA
    
    csv = df.to_csv(index=False)

    st.download_button(
        label=" Download Cleaned Dataset",
        data=csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv"
    )