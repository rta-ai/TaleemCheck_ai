"""
TaleemCheck AI - AI Evaluation Engine
Handles all Groq API calls: evaluation, vision OCR, rubric parsing.
"""

import json
import base64
import re
import streamlit as st
from groq import Groq
from utils.prompts import (
    get_evaluation_prompt,
    get_ocr_prompt,
    get_rubric_parse_prompt,
    get_class_summary_prompt,
)


def get_groq_client(api_key: str) -> Groq:
    """Initialize Groq client with provided API key."""
    return Groq(api_key=api_key)


def clean_json_response(text: str) -> str:
    """Strip markdown fences and whitespace from LLM JSON response."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def evaluate_answer(
    client: Groq,
    question: str,
    max_marks: int,
    rubric: str,
    student_answer: str,
    model: str = "llama-3.3-70b-versatile",
) -> dict:
    """
    Evaluate a single student answer using Groq LLM.
    Returns structured evaluation dict.
    """
    prompt = get_evaluation_prompt(question, max_marks, rubric, student_answer)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,  # Low temp for deterministic grading
            max_tokens=1500,
        )
        raw = response.choices[0].message.content
        cleaned = clean_json_response(raw)
        result = json.loads(cleaned)

        # Validate and clamp marks
        result["marks_awarded"] = max(0, min(int(result.get("marks_awarded", 0)), max_marks))
        return result

    except json.JSONDecodeError as e:
        return {
            "marks_awarded": 0,
            "marks_justification": "Error parsing AI response.",
            "strengths": ["Could not evaluate"],
            "missing_concepts": ["Evaluation failed"],
            "mistakes": ["JSON parse error"],
            "improvement_suggestions": ["Please retry"],
            "feedback_english": "AI evaluation failed. Please retry.",
            "feedback_roman_urdu": "AI evaluation fail ho gayi. Dobara koshish karein.",
            "concept_tags": ["error"],
            "error": str(e),
        }
    except Exception as e:
        return {
            "marks_awarded": 0,
            "marks_justification": f"API Error: {str(e)}",
            "strengths": ["N/A"],
            "missing_concepts": ["N/A"],
            "mistakes": ["API call failed"],
            "improvement_suggestions": ["Check API key and retry"],
            "feedback_english": f"Evaluation failed: {str(e)}",
            "feedback_roman_urdu": "Kuch masla aa gaya. API check karein.",
            "concept_tags": ["error"],
            "error": str(e),
        }


def extract_text_from_image(client: Groq, image_bytes: bytes, image_type: str = "image/jpeg") -> str:
    """
    Use Groq Vision model to extract text from handwritten/printed image.
    Returns extracted text string.
    """
    try:
        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        prompt = get_ocr_prompt()

        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_type};base64,{b64_image}"
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            temperature=0.1,
            max_tokens=2000,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[OCR Error: {str(e)}]"


def parse_rubric_document(client: Groq, raw_text: str, model: str = "llama-3.3-70b-versatile") -> list:
    """
    Parse uploaded question paper / rubric text into structured question list.
    Returns list of question dicts.
    """
    prompt = get_rubric_parse_prompt(raw_text)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000,
        )
        raw = response.choices[0].message.content
        cleaned = clean_json_response(raw)
        questions = json.loads(cleaned)
        return questions if isinstance(questions, list) else []

    except Exception as e:
        st.error(f"Failed to parse rubric document: {e}")
        return []


def generate_class_summary(client: Groq, analytics_data: dict, model: str = "llama-3.3-70b-versatile") -> str:
    """
    Generate AI-powered class performance summary for the teacher.
    """
    data_str = json.dumps(analytics_data, indent=2)
    prompt = get_class_summary_prompt(data_str)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not generate summary: {e}"


def batch_evaluate_student(
    client: Groq,
    student_name: str,
    student_answers: list,
    questions: list,
    model: str = "llama-3.3-70b-versatile",
    progress_callback=None,
) -> list:
    """
    Evaluate all answers for a single student.
    Returns list of evaluation results.
    """
    results = []
    for i, (q, ans) in enumerate(zip(questions, student_answers)):
        if progress_callback:
            progress_callback(i, len(questions), student_name, q.get("question_number", f"Q{i+1}"))

        result = evaluate_answer(
            client=client,
            question=q.get("question", ""),
            max_marks=q.get("max_marks", 5),
            rubric=q.get("rubric", ""),
            student_answer=ans,
            model=model,
        )
        result["question_number"] = q.get("question_number", f"Q{i+1}")
        result["question"] = q.get("question", "")
        result["max_marks"] = q.get("max_marks", 5)
        result["student_name"] = student_name
        results.append(result)

    return results
