import streamlit as st
from google import genai
from PyPDF2 import PdfReader

# --- CONFIGURATION ---
# We get the key from the secret vault
api_key = st.secrets["GOOGLE_API_KEY"]

# NEW: We use the 'Client' method for the new SDK
client = genai.Client(api_key=api_key)

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

# --- THE APP UI ---
st.set_page_config(page_title="HOA Bylaw Search", layout="wide")

st.title("🏡 HOA Document Search Engine")
st.subheader("Upload your CC&Rs, Bylaws, and Meeting Minutes. Ask anything.")

# Sidebar
with st.sidebar:
    st.header("Your Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF Files", accept_multiple_files=True, type="pdf"
    )
    process_button = st.button("Analyze Documents")

# State Management
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""

# Processing
if process_button and uploaded_files:
    with st.spinner("Reading your HOA documents..."):
        raw_text = get_pdf_text(uploaded_files)
        st.session_state.pdf_content = raw_text
        st.success("Documents Loaded! You can now search.")

# Chat Logic
user_question = st.text_input("Ask a question about the rules (e.g., 'Can I paint my fence blue?')")

if user_question:
    if not st.session_state.pdf_content:
        st.warning("Please upload documents first!")
    else:
        # Display User Message
        st.info(f"You asked: {user_question}")
        
        # The Prompt
        prompt = f"""
        You are an expert HOA attorney assistant. 
        Answer the question based STRICTLY on the text provided below.
        
        Rules:
        1. Quote the specific Article or Section number.
        2. If the answer is not in the text, say "I cannot find a rule about that."
        
        USER QUESTION: {user_question}
        
        HOA DOCUMENTS TEXT:
        {st.session_state.pdf_content}
        """
        
        # Generate Answer using the NEW method
        with st.spinner("Searching the bylaws..."):
            try:
                # We use the model found in your diagnostic script
                response = client.models.generate_content(
    model="gemini-flash-latest", 
    contents=prompt
)
                st.success(response.text)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.caption("Powered by Gemini 2.0 Flash")




