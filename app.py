from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pdfplumber
import docx
from sentence_transformers import SentenceTransformer, util
import re

app = Flask(__name__)
CORS(app)

model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_candidate_details(resume_text):
    """Extracts name, phone number, and email from resume text."""
    name = resume_text.split("\n")[0]  # First line as fallback name
    
    phone_match = re.search(r'\b\d{10}\b', resume_text)  # Find 10-digit phone number
    phone = phone_match.group() if phone_match else "Not found"
    
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)  # Find email
    email = email_match.group() if email_match else "Not found"
    
    return {"name": name, "phone": phone, "email": email}

@app.route("/rank-resumes", methods=["POST"])
def rank_resumes():
    try:
        job_description = request.form.get("job_description", "").strip()
        uploaded_files = request.files.getlist("files")

        if not job_description or not uploaded_files:
            return jsonify({"error": "Provide job description and at least one resume file"}), 400

        extracted_resumes = []
        candidate_details = []

        for file in uploaded_files:
            file_path = os.path.join("uploads", file.filename)
            file.save(file_path)

            if file.filename.endswith(".pdf"):
                resume_text = extract_text_from_pdf(file_path)
            elif file.filename.endswith(".docx"):
                resume_text = extract_text_from_docx(file_path)
            else:
                os.remove(file_path)
                continue

            os.remove(file_path)  # Cleanup after reading

            details = extract_candidate_details(resume_text)
            extracted_resumes.append(resume_text)
            candidate_details.append(details)

        job_embedding = model.encode(job_description, convert_to_tensor=True)
        resume_embeddings = model.encode(extracted_resumes, convert_to_tensor=True)
        
        scores = [util.pytorch_cos_sim(job_embedding, emb).item() for emb in resume_embeddings]
        ranked_resumes = sorted(zip(candidate_details, scores), key=lambda x: x[1], reverse=True)

        response = [
            {
                "rank": i + 1,
                "name": r[0]["name"],
                "phone": r[0]["phone"],
                "email": r[0]["email"],
                "score": round(r[1], 4)
            }
            for i, r in enumerate(ranked_resumes)
        ]

        return jsonify({"ranked_resumes": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)




