import os
import logging
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer, util

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

@app.route('/rank', methods=['POST'])
def rank_resumes():
    try:
        data = request.get_json()

        # Validate request format
        if not data or "job_description" not in data or "resumes" not in data:
            logging.error("Invalid request format")
            return jsonify({"error": "Invalid input. 'job_description' and 'resumes' are required."}), 400

        job_description = data["job_description"]
        resumes = data["resumes"]

        # Validate that inputs are not empty
        if not job_description.strip():
            return jsonify({"error": "Job description cannot be empty."}), 400
        if not isinstance(resumes, list) or not resumes:
            return jsonify({"error": "Resumes must be a non-empty list."}), 400

        # Encode job description and resumes
        job_embedding = model.encode(job_description, convert_to_tensor=True)
        resume_embeddings = [model.encode(resume, convert_to_tensor=True) for resume in resumes]

        # Compute similarity scores
        scores = [util.pytorch_cos_sim(job_embedding, resume_embedding).item() for resume_embedding in resume_embeddings]

        # Rank resumes based on similarity scores
        ranked_resumes = sorted(zip(resumes, scores), key=lambda x: x[1], reverse=True)

        # Format response
        result = [
            {"rank": i + 1, "resume": resume, "score": round(score, 4)}
            for i, (resume, score) in enumerate(ranked_resumes)
        ]

        logging.info("Resumes ranked successfully")
        return jsonify({"ranked_resumes": result}), 200

    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

