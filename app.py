import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# --- CONFIGURATION ---
api_key = st.secrets["GOOGLE_API_KEY"]

# We add 'transport="rest"' to fix connection issues
genai.configure(api_key=api_key, transport="rest") 

# Use the simple Flash name
model = genai.GenerativeModel('gemini-1.5-flash')

# This function reads the PDF file
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# --- THIS IS THE WEBSITE PART ---
st.set_page_config(page_title="HOA Helper", layout="wide")

st.title("🏡 HOA Document Search")
st.write("Upload your PDF rules (CC&Rs, Bylaws) and ask questions.")

# The Sidebar (Left side of screen)
with st.sidebar:
    st.header("1. Upload Docs")
    uploaded_files = st.file_uploader(
        "Choose PDF files", accept_multiple_files=True, type="pdf"
    )
    process_button = st.button("Read Documents")

# The Memory (Remembering what we uploaded)
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""

# What happens when you click "Read Documents"
if process_button and uploaded_files:
    with st.spinner("Reading... please wait..."):
        # Extract text from PDF
        raw_text = get_pdf_text(uploaded_files)
        st.session_state.pdf_content = raw_text
        st.success("Done! I have read the files.")

# The Chat Box
user_question = st.text_input("2. Ask a question (e.g., Can I paint my fence blue?)")

if user_question:
    if st.session_state.pdf_content == "":
        st.error("Please upload a PDF first!")
    else:
        # This sends your question + the PDF text to Gemini
        prompt = f"""
        You are a helpful assistant for a Homeowners Association (HOA).
        Answer the question based ONLY on the text below.
        If the answer is found, quote the rule number.
        
        QUESTION: {user_question}
        
        DOCUMENT TEXT:
        {st.session_state.pdf_content}
        """
        
        with st.spinner("Thinking..."):
            response = model.generate_content(prompt, generation_config={"temperature": 0})

            st.write(response.text)


