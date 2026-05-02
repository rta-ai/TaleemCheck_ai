"""
TaleemCheck AI - Prompt Engineering Module
All LLM prompts centralized here for easy modification.
"""

def get_evaluation_prompt(question: str, max_marks: int, rubric: str, student_answer: str) -> str:
    return f"""You are an experienced and fair university examiner in Pakistan.

Your task is to evaluate a student's answer based on the given rubric.

---
QUESTION:
{question}

MAXIMUM MARKS: {max_marks}

RUBRIC / MARKING SCHEME:
{rubric}

STUDENT'S ANSWER:
{student_answer}
---

Evaluate the answer carefully and fairly. Be strict but constructive.

Return ONLY a valid JSON object (no extra text, no markdown):

{{
  "marks_awarded": <integer between 0 and {max_marks}>,
  "marks_justification": "<brief reason for marks given>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "missing_concepts": ["<missing concept 1>", "<missing concept 2>"],
  "mistakes": ["<mistake 1>", "<mistake 2>"],
  "improvement_suggestions": ["<suggestion 1>", "<suggestion 2>"],
  "feedback_english": "<2-3 sentence constructive feedback in simple English>",
  "feedback_roman_urdu": "<2-3 sentence feedback in Roman Urdu e.g. Aap ka jawab theek tha lekin...>",
  "concept_tags": ["<topic tag 1>", "<topic tag 2>"]
}}

Rules:
- marks_awarded must be integer, 0 to {max_marks}.
- If answer is blank or irrelevant, award 0.
- concept_tags = core topics tested.
- feedback_roman_urdu must be Roman Urdu (English letters, Urdu words). NOT Urdu script.
- All lists must have at least one item.
- Return ONLY the JSON object, nothing else.
"""


def get_ocr_prompt() -> str:
    return """You are an OCR assistant. Extract all handwritten or printed text from this image exactly as written.

Instructions:
- Extract ALL visible text.
- Preserve structure and order.
- Keep question numbers if present.
- Do not add commentary or explanation.
- If text is unclear, write [unclear].
- Return ONLY the extracted text, nothing else.
"""


def get_rubric_parse_prompt(raw_text: str) -> str:
    return f"""You are an educational document parser.

Parse the following question paper or rubric and extract all questions.

DOCUMENT:
{raw_text}

Return ONLY a valid JSON array (no extra text):

[
  {{
    "question_number": "Q1",
    "question": "<full question text>",
    "max_marks": <integer>,
    "rubric": "<key points/concepts expected in answer>"
  }}
]

Rules:
- If max_marks not found, default to 5.
- If rubric not found, write "Award marks based on completeness and accuracy."
- Extract ALL questions.
- Return ONLY the JSON array.
"""


def get_class_summary_prompt(analytics_data: str) -> str:
    return f"""You are an educational analyst. Based on this class performance data, write a brief teacher summary.

DATA:
{analytics_data}

Write 3-4 sentences covering: overall performance, strongest areas, weakest areas, and one recommendation.
Return ONLY the summary text.
"""
