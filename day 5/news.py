import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import DuckDuckGoSearchRun
from langchain.callbacks import StdOutCallbackHandler
import logging
import time
from functools import wraps
import threading

# Suppress verbose logs
logging.getLogger().setLevel(logging.ERROR)

# Hardcoded Gemini API key
GEMINI_API_KEY = "AIzaSyAtOLnwK0PqWnrdMvVNJgMwWGi7H2ka_qI"  # Replace with your actual Gemini API key

# Rate limiting configuration (15 requests per minute, based on free-tier limits)
REQUESTS_PER_MINUTE = 15
SECONDS_PER_REQUEST = 60.0 / REQUESTS_PER_MINUTE
last_request_time = 0.0
lock = threading.Lock()

# Rate limiting decorator
def rate_limit(rpm):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global last_request_time
            with lock:
                current_time = time.time()
                time_since_last = current_time - last_request_time
                if time_since_last < SECONDS_PER_REQUEST:
                    time.sleep(SECONDS_PER_REQUEST - time_since_last)
                last_request_time = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Streamlit page configuration
st.set_page_config(page_title="Current Events Q&A", page_icon="🌍")
st.title("🌍 Current Events Q&A")
st.markdown("""
Ask any question about recent events or facts, and get answers powered by Google's Gemini model and real-time web search!  
Type your question below and hit the "Ask" button. 🚀
""")

# Initialize session state for chat history and request counter
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "request_count" not in st.session_state:
    st.session_state.request_count = 0
if "last_reset_time" not in st.session_state:
    st.session_state.last_reset_time = time.time()

# Function to check and reset request counter
def check_reset_counter():
    current_time = time.time()
    if current_time - st.session_state.last_reset_time >= 60:  # Reset every minute
        st.session_state.request_count = 0
        st.session_state.last_reset_time = current_time
    return st.session_state.request_count < REQUESTS_PER_MINUTE

# Function to initialize the agent
@st.cache_resource
def init_agent():
    try:
        # Initialize Gemini LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.7
        )
        # Initialize DuckDuckGo search tool
        tools = [DuckDuckGoSearchRun()]
        # Initialize agent with ZERO_SHOT_REACT_DESCRIPTION
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,  # Suppress verbose output
            callbacks=[StdOutCallbackHandler()]  # Minimal callbacks
        )
        return agent
    except Exception as e:
        if "API_KEY_INVALID" in str(e):
            st.error("❌ Gemini API key is invalid or expired. Please update the GEMINI_API_KEY in the code.")
        else:
            st.error(f"❌ Failed to initialize agent: {str(e)}")
        return None

# Rate-limited function to process questions
@rate_limit(rpm=REQUESTS_PER_MINUTE)
def process_question(question):
    try:
        agent = init_agent()
        if not agent:
            return None
        response = agent.run(question)
        return response
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return "❌ Rate limit exceeded. Please wait a minute and try again."
        elif "API_KEY_INVALID" in str(e):
            return "❌ Gemini API key is invalid or expired. Please update the GEMINI_API_KEY in the code."
        else:
            return f"❌ Error processing question: {str(e)}"

# User input interface
with st.form(key="question_form"):
    user_question = st.text_input("Your Question:", placeholder="e.g., What happened in the world today?")
    submit_button = st.form_submit_button("Ask 📩")

# Process user question
if submit_button and user_question:
    with st.spinner("🔍 Fetching answer..."):
        if check_reset_counter():
            response = process_question(user_question)
            if response:
                st.session_state.chat_history.append(("You", user_question))
                st.session_state.chat_history.append(("Bot", response))
                st.session_state.request_count += 1
            else:
                st.error("❌ Unable to process question. Agent initialization failed.")
        else:
            st.error("❌ Rate limit reached for this minute. Please wait and try again.")

# Display chat history
st.subheader("💬 Chat History")
if st.session_state.chat_history:
    for speaker, text in st.session_state.chat_history:
        if speaker == "You":
            st.markdown(f"**You**: {text}")
        else:
            st.markdown(f"**Bot**: {text}")
else:
    st.info("No questions asked yet. Start by typing a question above! 😊")

# Display request counter
st.markdown(f"**Requests this minute**: {st.session_state.request_count}/{REQUESTS_PER_MINUTE}")

# Setup instructions
