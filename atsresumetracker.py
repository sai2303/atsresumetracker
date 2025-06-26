
import streamlit as st
import google.generativeai as genai
import os
import pdfplumber
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(prompt, resume_text, user_query=None):
    """Send data to Gemini API and get response."""
    if not resume_text.strip():
        return "Error: Resume text is missing."
    
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        # Replace placeholders; use empty string if user_query is None
        input_data = prompt.replace("{text}", resume_text).replace("{jd}", user_query or "")
        response = model.generate_content(input_data)
        if response and response.text:
            return response.text.strip()
        return "No valid response from Gemini API."
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

def input_pdf_text(uploaded_file):
    """Extract and clean text from PDF using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
        if not text.strip():
            return "Error: No text found in PDF."
        
        # Clean up text
        text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
        text = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", text)
        text = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", text)
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
        cleaned_text = " ".join(text.split())
        return cleaned_text
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

# Streamlit UI
st.title("Smart ATS")
st.text("Improve Your Resume ATS")

jd = st.text_area("Paste the Job Description (required for some features)")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload a PDF")

col1, col2 = st.columns(2)
submit1 = col1.button("Tell Me About the Resume")
submit2 = col2.button("How Can I Improve My Skills")

col3, col4 = st.columns(2)
submit3 = col3.button("What Keywords Are Missing?")
submit4 = col4.button("Percentage Match")

input_prompt = st.text_input("Queries: Feel Free to Ask Here")
submit5 = st.button("Answer My Query")

# Define prompts
input_prompt1 = "Analyze the resume in {text} and provide strengths & weaknesses and keep it to the point.."
input_prompt2 = "Analyze the resume in {text} and suggest skill improvements based on {jd} if provided, otherwise general suggestions and keep it to the point.."
input_prompt3 = "Given the resume {text} and job description {jd}, identify keywords present in the job description but missing from the resume and keep it to the point.."
input_prompt4 = "Calculate a match percentage for the resume {text} against the job description {jd} and list missing keywords and keep it to the point."
input_prompt5 = "{jd}"  # Custom query

# Process uploaded file
resume_text = None
if uploaded_file:
    resume_text = input_pdf_text(uploaded_file)

# Handle button actions
if resume_text:
    if submit1:
        response = get_gemini_response(input_prompt1, resume_text)
        st.subheader("Analysis Result")
        st.write(response)
    
    elif submit2:
        response = get_gemini_response(input_prompt2, resume_text, jd)
        st.subheader("Improvement Suggestions")
        st.write(response)
    
    elif submit3:
        if not jd.strip():
            st.error("Please provide a job description to identify missing keywords.")
        else:
            response = get_gemini_response(input_prompt3, resume_text, jd)
            st.subheader("Missing Keywords")
            st.write(response)
    
    elif submit4:
        if not jd.strip():
            st.error("Please provide a job description to calculate the match percentage.")
        else:
            response = get_gemini_response(input_prompt4, resume_text, jd)
            st.subheader("Match Percentage & Recommendations")
            st.write(response)
    
    elif submit5:
        if not input_prompt.strip():
            st.error("Please enter a query to proceed.")
        else:
            response = get_gemini_response(input_prompt5, resume_text, input_prompt)
            st.subheader("Response")
            st.write(response)
else:
    if any([submit1, submit2, submit3, submit4, submit5]):
        st.warning("Please upload a PDF file to proceed.")
