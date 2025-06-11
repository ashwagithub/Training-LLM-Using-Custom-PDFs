import streamlit as st
import speech_recognition as sr
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from PIL import Image  
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import concurrent.futures

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize session state for toggling login/signup forms
if "login_active" not in st.session_state:
    st.session_state.login_active = False
if "signup_active" not in st.session_state:
    st.session_state.signup_active = False
if "login_toggle" not in st.session_state:
    st.session_state.login_toggle = False
if "signup_toggle" not in st.session_state:
    st.session_state.signup_toggle = False

# -------------------------------
# Parallelized File Extraction Functions
# -------------------------------
def extract_pdf_text(pdf_file):
    pdf_file.seek(0)
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted
    return text

def get_pdf_text(pdf_docs):
    text = ""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(extract_pdf_text, pdf_docs)
    for res in results:
        text += res
    return text

def extract_image_text(image_file):
    img = Image.open(image_file)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([
        "Extract all text from this image. Return only the raw text without any formatting or analysis.",
        img
    ])
    return response.text + "\n"

def get_image_text(uploaded_images):
    image_text = ""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(extract_image_text, uploaded_images)
    for res in results:
        image_text += res
    return image_text

# -------------------------------
# Caching Expensive Operations
# -------------------------------
@st.cache_data(show_spinner=False)
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    return vector_store

def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context. If the answer is not in the context, just say, "answer is not available in the context."
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(user_question):
    # Check for simple greetings and respond directly
    greetings = {"hi", "hello", "hey", "hii", "welcome"}
    if user_question.strip().lower() in greetings:
        return "Hello! How can I help you today?"
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    # Check if the FAISS index exists locally
    if os.path.exists("faiss_index"):
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)
    else:
        docs = []
    
    chain = get_conversational_chain()
    
    if docs:
        response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
        return response["output_text"]
    else:
        # Fallback: directly answer the question using the generative AI model
        ai_model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
        response = ai_model.generate_content([user_question])
        return response.text

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now!")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            st.success(f"Recognized Speech: {text}")
            return text
        except sr.UnknownValueError:
            st.warning("Could not understand the audio")
        except sr.RequestError:
            st.error("Could not request results, check your internet connection")
    return ""

def main():
    st.set_page_config(page_title="Chat with PDFs & Images + Voice Input", layout="wide")
    
    # CSS styling (layout and background color remain unchanged; text input styling remains as your original)
    st.markdown("""
    <style>
        /* Import the Lobster font from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Lobster&display=swap');

        /* Global style for all buttons */
        div.stButton button {
            background-color: red !important;
            color: white !important;
            border-radius: 8px;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }
        div.stButton button:hover {
            background-color: #ff6666 !important;
            transform: scale(1.05);
        }
        /* Text input styling (original) */
        div.stTextInput input {
            height: 40px;
            font-size: 16px;
        }
        /* Voice button styling */
        .voice-container button {
            height: 40px !important;
            padding: 0 10px !important;
            font-size: 16px !important;
            margin: 0 !important;
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 100px !important;
        }
        /* Sidebar Submit button: full width */
        [data-testid='stSidebar'] .stButton button.submit-btn {
            width: 100%;
            margin-bottom: 10px;
        }
        /* Styling for the file uploader container */
        div[data-testid="stFileUploader"] {
            border: 2px solid #ff6666;
            border-radius: 10px;
            padding: 10px;
        }
        /* Inline styling for Login and Signup buttons */
        .auth-inline-container {
            display: flex;
            gap: 2px;
        }
        .auth-inline-container > div {
            flex: 1;
            padding: 0;
            margin: 0;
        }
        .auth-inline-container button {
            width: 100% !important;
            background-color: red !important;
            color: white !important;
            border: none;
            border-radius: 8px;
            padding: 5px 10px;
            font-size: 14px;
            transition: background-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
        }
        .auth-inline-container button:hover {
            background-color: #ff6666 !important;
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        /* Overall layout: border radius and subtle box shadow for main container and sidebar */
        [data-testid="stAppViewContainer"] {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        [data-testid="stSidebar"] {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        /* Align main input row vertically */
        [data-testid="stHorizontalBlock"] {
            display: flex;
            align-items: center;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 style='font-family: \"Lobster\", cursive; color: white; text-align: left; font-weight: bold;'>📚BDCOE_Study_Buddy</h1>", unsafe_allow_html=True)
    
    # Create a placeholder for upload messages at the top of the sidebar
    upload_placeholder = st.sidebar.empty()
    upload_placeholder.title("📂 Upload PDFs & Images")
    uploaded_files = st.sidebar.file_uploader("Upload PDFs & Images", accept_multiple_files=True, type=["pdf", "png", "jpg", "jpeg"])
    
    if st.sidebar.button("Submit & Process", key="submit_button"):
        with st.spinner("Processing..."):
            combined_text = ""
            pdf_files = [file for file in uploaded_files if file.type == "application/pdf"]
            image_files = [file for file in uploaded_files if file.type.startswith("image/")]
            if pdf_files:
                combined_text += get_pdf_text(pdf_files)
            if image_files:
                combined_text += get_image_text(image_files)
            text_chunks = get_text_chunks(combined_text)
            get_vector_store(text_chunks)
            upload_placeholder.success("Processing Done!")
    
    with st.sidebar.container():
        st.markdown("<div class='auth-inline-container'>", unsafe_allow_html=True)
        col_login, col_signup = st.columns(2)
        if col_login.button("🔑 Login", key="login_button"):
            st.session_state.login_toggle = not st.session_state.login_toggle
            st.session_state.login_active = st.session_state.login_toggle
            if st.session_state.login_active:
                st.session_state.signup_active = False
                st.session_state.signup_toggle = False
        if col_signup.button("📝 Signup", key="signup_button"):
            st.session_state.signup_toggle = not st.session_state.signup_toggle
            st.session_state.signup_active = st.session_state.signup_toggle
            if st.session_state.signup_active:
                st.session_state.login_active = False
                st.session_state.login_toggle = False
        st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.login_active:
        with st.sidebar.form("login_form", clear_on_submit=True):
            st.write("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                st.sidebar.success(f"Logged in as {username}")
                st.session_state.login_active = False
                st.session_state.login_toggle = False
    
    if st.session_state.signup_active:
        with st.sidebar.form("signup_form", clear_on_submit=True):
            st.write("Signup")
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Signup")
            if submitted:
                if new_password == confirm_password:
                    st.sidebar.success("Account created successfully!")
                else:
                    st.sidebar.error("Passwords do not match")
                st.session_state.signup_active = False
                st.session_state.signup_toggle = False
    
    # Original text box interface for Q&A with feedback
    col1, col2 = st.columns([8, 2])
    with col1:
        user_question = st.text_input("", placeholder="Type your question here...", key="question_input", label_visibility="collapsed")
    with col2:
        with st.container():
            if st.button("🎙 Voice", key="voice_button"):
                recognized_text = recognize_speech()
                if recognized_text:
                    user_question = recognized_text  
    if user_question:
        answer = user_input(user_question)
        st.write("Reply:", answer)
        col_feedback1, col_feedback2 = st.columns(2)
        if col_feedback1.button("👍", key="feedback_up"):
            st.success("Feedback recorded: Positive")
        if col_feedback2.button("👎", key="feedback_down"):
            st.success("Feedback recorded: Negative")

if __name__ == "__main__":
    main()
