"""
TaleemCheck AI - Document Parser Module
Handles text extraction from PDF, TXT, DOCX files.
"""

import io
import streamlit as st


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file using PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except ImportError:
        return "[PyMuPDF not installed. Please install pymupdf.]"
    except Exception as e:
        return f"[PDF Error: {str(e)}]"


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs).strip()
    except ImportError:
        return "[python-docx not installed. Please install python-docx.]"
    except Exception as e:
        return f"[DOCX Error: {str(e)}]"


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extract text from a plain text file."""
    try:
        return file_bytes.decode("utf-8").strip()
    except UnicodeDecodeError:
        try:
            return file_bytes.decode("latin-1").strip()
        except Exception as e:
            return f"[TXT Error: {str(e)}]"


def extract_text_from_file(uploaded_file) -> str:
    """
    Auto-detect file type and extract text.
    Supports: PDF, TXT, DOCX
    """
    if uploaded_file is None:
        return ""

    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif file_name.endswith(".txt"):
        return extract_text_from_txt(file_bytes)
    elif file_name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        return f"[Unsupported file type: {uploaded_file.name}]"


def get_image_bytes_and_type(uploaded_file) -> tuple:
    """
    Return (bytes, mime_type) for an uploaded image file.
    """
    if uploaded_file is None:
        return None, None

    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".png"):
        return file_bytes, "image/png"
    elif file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
        return file_bytes, "image/jpeg"
    elif file_name.endswith(".webp"):
        return file_bytes, "image/webp"
    else:
        return file_bytes, "image/jpeg"  # default


def parse_manual_answers(raw_text: str, num_questions: int) -> list:
    """
    Parse pasted student answers.
    Tries to split by Q1, Q2... or numbered lines.
    Falls back to splitting by double newlines.
    """
    import re

    # Try to match Q1:, Q2:, 1., 2. patterns
    pattern = r"(?:Q\d+[:.)\s]|\d+[:.)\s])"
    parts = re.split(pattern, raw_text, flags=re.IGNORECASE)
    parts = [p.strip() for p in parts if p.strip()]

    if len(parts) >= num_questions:
        return parts[:num_questions]

    # Fallback: split by double newlines
    parts = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
    if len(parts) >= num_questions:
        return parts[:num_questions]

    # Fallback: treat entire text as one answer, pad rest with empty
    answers = [raw_text.strip()] + [""] * (num_questions - 1)
    return answers[:num_questions]
