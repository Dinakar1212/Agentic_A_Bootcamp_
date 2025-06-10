import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key="AIzaSyAW4RWVlWh9Z1xDH-KaNyAjWhOmeYo1q6A")
model = genai.GenerativeModel('gemini-1.5-flash')

# Streamlit app
st.title("Resume Generator")
st.write("Enter your details below to generate an ATS-friendly professional resume as a PDF.")

# User input form
with st.form("resume_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    city_state = st.text_input("City, State (e.g., Springfield, IL)")
    linkedin = st.text_input("LinkedIn Profile URL (Optional)")
    portfolio = st.text_input("Portfolio URL (Optional)")
    
    st.subheader("Profile (Summary/Objective)")
    profile = st.text_area("Enter a 2-3 sentence professional summary (for experienced professionals) or objective (for entry-level/career changers). Example: 'Highly motivated Software Engineer with 5 years of experience in Python and cloud computing.'")
    
    st.subheader("Education")
    education = st.text_area("Enter education details (e.g., Degree, Institution, Year, GPA if 3.5+, Relevant Coursework)")
    
    st.subheader("Work Experience")
    experience = st.text_area("Enter work experience (e.g., Job Title, Company, City, State, Duration, Responsibilities with quantifiable achievements)")
    
    st.subheader("Projects")
    projects = st.text_area("Enter project details (e.g., Project Name, Description, Technologies, Outcome)")
    
    st.subheader("Skills")
    skills = st.text_area("Enter skills (e.g., Technical: Python, SQL; Soft: Communication, Leadership; Languages: Spanish (Fluent))")
    
    st.subheader("Awards and Recognition (Optional)")
    awards = st.text_area("Enter awards (e.g., Name of Award, Issuing Organization, Date, Brief Description)")
    
    submit_button = st.form_submit_button("Generate Resume")

# Function to create PDF from plain text
def create_pdf_resume(resume_text, name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.75*inch, leftMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    
    # Define custom styles
    header_style = ParagraphStyle(
        name='Header',
        fontSize=16,
        leading=20,
        fontName='Helvetica-Bold',
        alignment=1,  # Center
        spaceAfter=12
    )
    contact_style = ParagraphStyle(
        name='Contact',
        fontSize=10,
        leading=12,
        fontName='Helvetica',
        alignment=1,
        spaceAfter=12
    )
    section_style = ParagraphStyle(
        name='Section',
        fontSize=12,
        leading=14,
        fontName='Helvetica-Bold',
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        name='Body',
        fontSize=10,
        leading=12,
        fontName='Helvetica',
        spaceAfter=6,
        bulletFontName='Helvetica',
        bulletFontSize=10,
        leftIndent=20
    )
    
    story = []
    
    # Add header (name)
    story.append(Paragraph(name.upper(), header_style))
    
    # Add contact details
    contact_parts = [part for part in [phone, email, linkedin, portfolio, city_state] if part]
    contact_info = " | ".join(contact_parts)
    story.append(Paragraph(contact_info, contact_style))
    
    # Process resume text
    lines = resume_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Check if line is a section header (all uppercase)
        if line.isupper():
            story.append(Paragraph(line, section_style))
        elif line.startswith('-'):
            # Format bullet points
            bullet_text = line[1:].strip().replace('<br>', '')
            story.append(Paragraph(f"• {bullet_text}", body_style))
        else:
            # Regular text under section
            story.append(Paragraph(line, body_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Generate resume when form is submitted
if submit_button:
    if not all([name, email, phone, city_state, profile, education, experience, projects, skills]):
        st.error("Please fill in all required fields (LinkedIn, Portfolio, and Awards are optional).")
    else:
        # Prepare prompt for Gemini
        prompt = f"""
        Create an ATS-friendly professional resume based on the following details:
        
        Name: {name}
        Email: {email}
        Phone: {phone}
        City, State: {city_state}
        LinkedIn: {linkedin}
        Portfolio: {portfolio}
        
        Profile (Summary/Objective):
        {profile}
        
        Education:
        {education}
        
        Work Experience:
        {experience}
        
        Projects:
        {projects}
        
        Skills:
        {skills}
        
        Awards and Recognition:
        {awards}
        
        Format the resume as plain text in an ATS-friendly, clean, and professional layout with the following structure:
        
        [Name]
        [Phone] | [Email] | [LinkedIn (if provided)] | [Portfolio (if provided)] | [City, State]
        
        SUMMARY
        - [2-3 sentence summary or objective based on Profile input]
        
        SKILLS
        - [Technical skills, e.g., Python, SQL]
        - [Soft skills, e.g., Communication, Leadership]
        - [Languages, if provided, e.g., Spanish (Fluent)]
        
        EXPERIENCE
        [Job Title] | [Company Name] | [City, State]
        [Start Date] - [End Date]
        - [Achievement with action verb and quantifiable result]
        - [Another achievement]
        
        EDUCATION
        [Degree] | [Major] | [University] | [City, State]
        [Graduation Date]
        - [GPA, if 3.5+]
        - [Relevant Coursework, if provided]
        - [Awards/Honors, if provided]
        
        PROJECTS
        [Project Name] | [Brief Description] | [Link, if provided]
        [Date]
        - [Role, tools/technologies, outcome]
        
        AWARDS
        [Award Name] | [Issuing Organization] | [Date]
        - [Brief description]
        
        Use clear section headers in all uppercase (e.g., SUMMARY, SKILLS). Use hyphens ('-') for bullet points. Start experience and project bullets with action verbs (e.g., Led, Developed, Streamlined) and include quantifiable achievements where possible. Ensure readability without any markup (e.g., LaTeX, HTML). Exclude empty sections (e.g., AWARDS if no awards provided). Return only the resume content in plain text, without comments or explanations.
        """
        
        try:
            # Generate resume using Gemini
            response = model.generate_content(prompt)
            resume_text = response.text
            
            # Display the resume
            st.subheader("Generated Resume (Plain Text)")
            st.text_area("Resume Preview", resume_text, height=400)
            
            # Generate PDF
            pdf_data = create_pdf_resume(resume_text, name)
            
            # Provide download options
            st.subheader("Download Options")
            st.download_button(
                label="Download Resume PDF",
                data=pdf_data,
                file_name=f"{name}_resume.pdf",
                mime="application/pdf"
            )
            st.download_button(
                label="Download Resume Text",
                data=resume_text,
                file_name=f"{name}_resume.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"Error generating resume: {str(e)}")
