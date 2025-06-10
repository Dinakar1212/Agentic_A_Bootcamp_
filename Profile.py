import streamlit as st
import google.generativeai as genai
import os

# Configure Gemini API
genai.configure(api_key="AIzaSyAW4RWVlWh9Z1xDH-KaNyAjWhOmeYo1q6A")
model = genai.GenerativeModel('gemini-1.5-flash')

# Streamlit app
st.title("Resume Generator")
st.write("Enter your details below to generate a professional resume as plain text.")

# User input form
with st.form("resume_form"):
    name = st.text_input("Full Name")
    address = st.text_area("Address")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    
    st.subheader("Education")
    education = st.text_area("Enter education details (e.g., Degree, Institution, Year)")
    
    st.subheader("Work Experience")
    experience = st.text_area("Enter work experience (e.g., Job Title, Company, Duration, Responsibilities)")
    
    st.subheader("Projects")
    projects = st.text_area("Enter project details (e.g., Project Name, Description, Technologies)")
    
    st.subheader("Skills")
    skills = st.text_area("Enter skills (e.g., Programming Languages, Tools, Soft Skills)")
    
    submit_button = st.form_submit_button("Generate Resume")

# Generate resume when form is submitted
if submit_button:
    if not all([name, address, email, phone, education, experience, projects, skills]):
        st.error("Please fill in all fields.")
    else:
        # Prepare prompt for Gemini
        prompt = f"""
        Create a professional resume based on the following details:
        
        Name: {name}
        Address: {address}
        Email: {email}
        Phone: {phone}
        
        Education:
        {education}
        
        Work Experience:
        {experience}
        
        Projects:
        {projects}
        
        Skills:
        {skills}
        
        Format the resume as plain text in a clean, organized, and professional layout. Use clear section headers (e.g., EDUCATION, WORK EXPERIENCE) and bullet points (using '-') for key details. Ensure proper alignment and readability without any markup (e.g., LaTeX, HTML). Return only the resume content in plain text, without any comments or explanations.
        """
        
        try:
            # Generate resume using Gemini
            response = model.generate_content(prompt)
            resume_text = response.text
            
            # Display the resume
            st.subheader("Generated Resume (Plain Text)")
            st.text_area("Resume Preview", resume_text, height=400)
            
            # Provide download option
            st.download_button(
                label="Download Resume Text",
                data=resume_text,
                file_name=f"{name}_resume.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"Error generating resume: {str(e)}")