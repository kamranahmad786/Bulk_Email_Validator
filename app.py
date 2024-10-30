import streamlit as st
import pandas as pd
import re
from email_validator import validate_email, EmailNotValidError
import is_disposable_email
import base64

def create_download_link(df):
    """Generate a download link for the Excel file"""
    excel_file = df.to_excel(index=False)
    b64 = base64.b64encode(excel_file).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="verified_emails.xlsx">Download Excel File</a>'

def verify_email(email):
    """Verify a single email address"""
    result = {
        'Email': email,
        'Valid Email': 'Valid Email' if re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email) else 'Invalid Email',
        'Domain Address': email.split('@')[1] if '@' in email else 'Invalid',
        'Disposable Email': 'Yes' if is_disposable_email.check(email) else 'No',
        'Deliverable Email': 'No',
        'Reason': '-'
    }
    
    try:
        emailinfo = validate_email(email, check_deliverability=True)
        result['Deliverable Email'] = 'Yes'
    except EmailNotValidError as e:
        result['Reason'] = str(e)
    
    return result

def main():
    # Page configuration
    st.set_page_config(page_title="Email Validator", layout="wide")
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
        }
        .upload-box {
            border: 2px dashed #ccc;
            padding: 2rem;
            text-align: center;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("✉️ Email Validation Tool")
    st.markdown("---")
    
    # Two columns layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Single Email Verification")
        single_email = st.text_input("Enter email address")
        if st.button("Verify Single Email"):
            if single_email:
                result = verify_email(single_email)
                st.json(result)
            else:
                st.warning("Please enter an email address")
    
    with col2:
        st.subheader("Bulk Email Verification")
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                if 'Email' not in df.columns:
                    st.error("CSV must contain 'Email' column")
                else:
                    if st.button("Verify All Emails"):
                        progress_bar = st.progress(0)
                        results = []
                        for index, email in enumerate(df['Email']):
                            results.append(verify_email(email))
                            progress_bar.progress((index + 1)/len(df))
                        
                        results_df = pd.DataFrame(results)
                        st.success("Verification Complete!")
                        st.dataframe(results_df)
                        
                        # Download button
                        st.download_button(
                            label="Download Excel",
                            data=results_df.to_excel(index=False).encode(),
                            file_name="verified_emails.xlsx",
                            mime="application/vnd.ms-excel"
                        )
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()