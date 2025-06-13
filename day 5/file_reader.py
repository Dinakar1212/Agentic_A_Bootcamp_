import streamlit as st
import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import tempfile

# Set Gemini API key directly in the code
GEMINI_API_KEY = "AIzaSyAW4RWVlWh9Z1xDH-KaNyAjWhOmeYo1q6A"  # Replace with your actual Gemini API key

# Streamlit page configuration
st.set_page_config(page_title="PDF Chatbot with Gemini", page_icon="📄")
st.title("📄 PDF Chatbot with Gemini")
st.markdown("""
This app allows you to upload a PDF file and ask questions about its content.
Powered by LangChain and Google's Gemini model.
""")

# Sidebar for file upload
with st.sidebar:
    st.header("Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# Initialize session state for chat history and vector store
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "conversation" not in st.session_state:
    st.session_state.conversation = None

# Function to process the uploaded PDF
def process_pdf(file):
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file.read())
        tmp_file_path = tmp_file.name

    # Load and process the PDF
    loader = PyPDFLoader(tmp_file_path)
    documents = loader.load()
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    # Create embeddings and vector store
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(chunks, embeddings)
    
    # Clean up temporary file
    os.unlink(tmp_file_path)
    
    return vectorstore

# Function to initialize the conversation chain
def initialize_conversation(vectorstore):
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.7
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    conversation = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation

# Process the uploaded file
if uploaded_file:
    with st.spinner("Processing PDF..."):
        st.session_state.vectorstore = process_pdf(uploaded_file)
        st.session_state.conversation = initialize_conversation(st.session_state.vectorstore)
    st.success("PDF processed successfully! You can now ask questions.")

# Chat interface
st.header("Ask Questions")
user_question = st.text_input("Enter your question about the PDF:")

if user_question and st.session_state.conversation:
    with st.spinner("Generating response..."):
        response = st.session_state.conversation({"question": user_question})
        st.session_state.chat_history.append(("You", user_question))
        st.session_state.chat_history.append(("Bot", response["answer"]))

# Display chat history
st.subheader("Chat History")
for speaker, text in st.session_state.chat_history:
    if speaker == "You":
        st.markdown(f"**You**: {text}")
    else:
        st.markdown(f"**Bot**: {text}")

# Instructions for setup
