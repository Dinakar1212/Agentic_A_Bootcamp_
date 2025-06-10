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
    profile = st.text_area("Enter a 2-3 sentence professional summary or objective.")
    
    st.subheader("Education")
    education = st.text_area("Enter education details.")
    
    st.subheader("Work Experience")
    experience = st.text_area("Enter work experience.")
    
    st.subheader("Projects")
    projects = st.text_area("Enter project details.")
    
    st.subheader("Skills")
    skills = st.text_area("Enter skills.")
    
    st.subheader("Awards and Recognition")
    awards = st.text_area("Enter awards (Optional)")
    
    submit_button = st.form_submit_button("Generate Resume")

# Function to create PDF
def create_pdf_resume(resume_text, name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle(name='Header', fontSize=16, leading=20,
                                   fontName='Helvetica-Bold', alignment=1, spaceAfter=12)
    contact_style = ParagraphStyle(name='Contact', fontSize=10, leading=12,
                                   fontName='Helvetica', alignment=1, spaceAfter=12)
    section_style = ParagraphStyle(name='Section', fontSize=12, leading=14,
                                   fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle(name='Body', fontSize=10, leading=12,
                                 fontName='Helvetica', spaceAfter=6, bulletFontName='Helvetica',
                                 bulletFontSize=10, leftIndent=20)
    
    story = []
    story.append(Paragraph(name.upper(), header_style))
    contact_parts = [part for part in [phone, email, linkedin, portfolio, city_state] if part]
    contact_info = " | ".join(contact_parts)
    story.append(Paragraph(contact_info, contact_style))
    
    lines = resume_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.isupper():
            story.append(Paragraph(line, section_style))
        elif line.startswith('-'):
            bullet_text = line[1:].strip()
            story.append(Paragraph(f"• {bullet_text}", body_style))
        else:
            story.append(Paragraph(line, body_style))
        story.append(Spacer(1, 0.1 * inch))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Generate resume when form is submitted
if submit_button:
    if not all([name, email, phone, city_state, profile, education, experience, projects, skills]):
        st.error("Please fill in all required fields. LinkedIn, Portfolio, and Awards are optional.")
    else:
        exclude_awards_section = "Exclude the AWARDS section." if not awards.strip() else ""
        
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
- Summary or objective from the profile input.

SKILLS
- Technical skills
- Soft skills
- Languages

EXPERIENCE
Job Title | Company Name | City, State
Start Date - End Date
- Achievement bullet points with quantifiable results

EDUCATION
Degree | Major | University | City, State
Graduation Date
- GPA, coursework, or honors (if provided)

PROJECTS
Project Name | Description | Link (if provided)
Date
- Role, tools used, achievements

AWARDS
Award Name | Issuing Organization | Date
- Description (if provided)

Use all uppercase for section headers. Use hyphens for bullet points. Do not include HTML or markdown. Keep the format plain text. {exclude_awards_section}
Return only the resume content without explanations.
"""
        try:
            response = model.generate_content(prompt)
            resume_text = response.text
            
            st.subheader("Generated Resume (Plain Text)")
            st.text_area("Resume Preview", resume_text, height=400)
            
            pdf_data = create_pdf_resume(resume_text, name)
            
            st.subheader("Download Options")
            st.download_button(
                label="Download Resume PDF",
                data=pdf_data,
                file_name=f"{name.replace(' ', '_')}_resume.pdf",
                mime="application/pdf"
            )
            st.download_button(
                label="Download Resume Text",
                data=resume_text,
                file_name=f"{name.replace(' ', '_')}_resume.txt",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"Error generating resume: {str(e)}")
