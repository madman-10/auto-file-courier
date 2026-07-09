import streamlit as st
from main import process_file # main.py file where the process of handling the files is stored/created


# Page configuration
st.set_page_config(page_title="File to Encrypted PDF", page_icon="🔒")

st.title("🔒 File to Encrypted PDF Converter")
st.write("""
Upload a document or image, and this app will convert it to a PDF (if necessary) 
and encrypt it. **Note:** The password to open your PDF will be the **first 4 characters** of the name you provide.
""")

st.divider()

# Input Form
with st.form("file_processor_form"):
    st.subheader("1. Enter Details")
    user_name = st.text_input("Your Name", placeholder="e.g., John Doe", max_chars=50)
    
    st.subheader("2. Upload File")
    # Limiting to extensions supported by your backend
    uploaded_file = st.file_uploader(
        "Choose a file", 
        type=["jpg", "png", "txt", "pdf", "md"]
    )
    
    submit_button = st.form_submit_button("Encrypt & Process")

# Processing Logic
if submit_button:
    # Validation
    if not user_name:
        st.error("Please enter a name.")
    elif len(user_name) < 4:
        st.warning("Please enter a name with at least 4 characters for encryption.")
    elif not uploaded_file:
        st.error("Please upload a file to process.")
    else:
        with st.spinner("Processing and encrypting your file..."):
            # Call backend function
            result_bytes, message = process_file(uploaded_file, user_name)
            
            # Handle results
            if result_bytes:
                st.success(f"File processed successfully! ({message})")
                
                # Display password for user clarity
                password = user_name[:4].upper()
                st.info(f"🔑 **Important:** The password to open this PDF will be the first 4 letters of your name, all *caps*.")
                
                # Generate dynamic filename
                original_name = uploaded_file.name.rsplit('.', 1)[0]
                new_filename = f"{original_name}_encrypted.pdf"
                
                # Provide download button
                st.download_button(
                    label="⬇️ Download Encrypted PDF",
                    data=result_bytes,
                    file_name=new_filename,
                    mime="application/pdf",
                    type="primary"
                )
            else:
                st.error(f"Failed to process file: {message}")