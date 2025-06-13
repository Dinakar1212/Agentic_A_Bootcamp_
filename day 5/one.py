import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence

# Initialize Streamlit app
st.title("English to French Translator")
st.markdown("Enter an English sentence and get its French translation using Google Gemini!")

# Text input
sentence = st.text_input("Enter an English sentence:", placeholder="Type here...", key="input1")

# Prompt
system_prompt = "You are a professional translator. Translate the given English sentence to French accurately."
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "Translate this sentence to French: {sentence}")
])

# ✅ Hardcoded API key
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    google_api_key="AIzaSyAW4RWVlWh9Z1xDH-KaNyAjWhOmeYo1q6A"
)

# LangChain pipeline
chain: RunnableSequence = prompt | llm

# Button logic
if st.button("Translate"):
    if sentence.strip():
        try:
            result = chain.invoke({"sentence": sentence})
            translated_text = result.content.strip()
            st.success("Translation completed!")
            st.write("**French Translation:**")
            st.markdown(f"**{translated_text}**")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a valid sentence.")
