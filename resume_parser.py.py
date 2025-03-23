import openai
import json
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def extract_resume_data(resume_text):
    """Uses OpenAI API to extract key details from a resume."""
    prompt = f"""
    Extract the following details from this resume:
    - Candidate Name
    - Work Experience (Job Titles, Years of Experience)
    - Skills
    - Education (Degree, University, Year)
    
    Resume:\n{resume_text}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",  # You can also use "gpt-3.5-turbo" if needed
        messages=[{"role": "system", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]

# Example usage
resume_text = """John Doe
Software Engineer with 5 years of experience in Python, Flask, and AI development.
B.Sc. in Computer Science from XYZ University, 2019.
Skills: Python, Flask, Machine Learning, OpenAI API, SQL, REST APIs.
"""
parsed_data = extract_resume_data(resume_text)
print(parsed_data)

