"""
PDF Service - Extract text from PDF files
"""
import PyPDF2
from io import BytesIO


def extract_text_from_pdf(pdf_content: bytes) -> str:
    """
    Extract text content from PDF buffer

    Args:
        pdf_content: PDF file content as bytes

    Returns:
        Extracted text as string
    """
    try:
        pdf_file = BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        return text.strip()

    except Exception as e:
        print(f"PDF parsing error: {e}")
        raise Exception("Failed to extract text from PDF")
