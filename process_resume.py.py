import pdfplumber  # Library for extracting text from PDFs
import docx  # Library for extracting text from DOCX files
import os  # Library to handle file paths

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""  # Initialize an empty string to store text
    with pdfplumber.open(pdf_path) as pdf:  # Open PDF file
        for page in pdf.pages:  # Loop through each page
            text += page.extract_text() + "\n"  # Extract text and add newline
    return text.strip()  # Return extracted text without extra spaces

def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    doc = docx.Document(docx_path)  # Open the DOCX file
    text = "\n".join([para.text for para in doc.paragraphs])  # Extract all text
    return text.strip()

def extract_text(file_path):
    """Determine file type (PDF or DOCX) and extract text accordingly."""
    _, ext = os.path.splitext(file_path)  # Get file extension
    if ext.lower() == ".pdf":  # If file is a PDF
        return extract_text_from_pdf(file_path)
    elif ext.lower() == ".docx":  # If file is a DOCX
        return extract_text_from_docx(file_path)
    else:
        return "Unsupported file format"  # If file is neither PDF nor DOCX

# Test with a sample resume file
if __name__ == "__main__":
    sample_resume = "uploads/Priyanka_Resume.pdf"  # Change this to an actual file in your uploads folder
    extracted_text = extract_text(sample_resume)  # Extract text
    print("Extracted Text:\n", extracted_text)  # Print extracted text
