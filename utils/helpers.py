"""
TaleemCheck AI - Helpers & Utilities
Session state management, UI helpers, data utilities.
"""

import streamlit as st
import json
from datetime import datetime


# ─────────────────────────────────────────────
# SESSION STATE MANAGEMENT
# ─────────────────────────────────────────────

def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "api_key": "",
        "groq_model": "llama-3.3-70b-versatile",
        "questions": [],           # List of question dicts
        "students": [],            # List of student name strings
        "student_answers": {},     # {student_name: [answer1, answer2, ...]}
        "evaluation_results": {},  # {student_name: [result1, result2, ...]}
        "evaluation_done": False,
        "approved_marks": {},      # {student_name: {q_num: marks}}
        "current_page": "home",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def reset_evaluation():
    """Reset evaluation state (keep questions and students)."""
    st.session_state.evaluation_results = {}
    st.session_state.evaluation_done = False
    st.session_state.approved_marks = {}


def reset_all():
    """Full reset of all session state."""
    keys_to_clear = [
        "questions", "students", "student_answers",
        "evaluation_results", "evaluation_done", "approved_marks"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    init_session_state()


# ─────────────────────────────────────────────
# MARK APPROVAL HELPERS
# ─────────────────────────────────────────────

def get_approved_marks(student_name: str, question_number: str, ai_marks: int) -> int:
    """Get teacher-approved marks, falling back to AI marks."""
    return st.session_state.approved_marks.get(student_name, {}).get(question_number, ai_marks)


def set_approved_marks(student_name: str, question_number: str, marks: int):
    """Save teacher-approved marks to session state."""
    if student_name not in st.session_state.approved_marks:
        st.session_state.approved_marks[student_name] = {}
    st.session_state.approved_marks[student_name][question_number] = marks


def apply_approved_marks_to_results(results: dict, approved: dict) -> dict:
    """
    Merge teacher-approved marks back into results dict.
    Returns updated results.
    """
    updated = {}
    for student, q_results in results.items():
        updated[student] = []
        for qr in q_results:
            qr_copy = qr.copy()
            q_num = qr_copy.get("question_number", "")
            if student in approved and q_num in approved[student]:
                qr_copy["marks_awarded"] = approved[student][q_num]
                qr_copy["teacher_approved"] = True
            else:
                qr_copy["teacher_approved"] = False
            updated[student].append(qr_copy)
    return updated


# ─────────────────────────────────────────────
# DATA VALIDATION
# ─────────────────────────────────────────────

def validate_questions(questions: list) -> tuple[bool, str]:
    """Validate question list structure."""
    if not questions:
        return False, "No questions found. Please add at least one question."
    for i, q in enumerate(questions):
        if not q.get("question", "").strip():
            return False, f"Question {i+1} has no question text."
        if q.get("max_marks", 0) <= 0:
            return False, f"Question {i+1} has invalid max marks (must be > 0)."
    return True, "Valid"


def validate_students(students: list) -> tuple[bool, str]:
    """Validate student list."""
    if not students:
        return False, "No students added."
    if len(students) != len(set(students)):
        return False, "Duplicate student names found."
    return True, "Valid"


def validate_answers(student_answers: dict, students: list, num_questions: int) -> tuple[bool, str]:
    """Check that all students have answers for all questions."""
    for student in students:
        answers = student_answers.get(student, [])
        if len(answers) < num_questions:
            return False, f"Student '{student}' is missing answers."
    return True, "Valid"


# ─────────────────────────────────────────────
# UI HELPER COMPONENTS
# ─────────────────────────────────────────────

def metric_card(label: str, value: str, delta: str = "", color: str = "#3498DB"):
    """Render a styled metric card."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {color}22, {color}11);
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 16px 20px;
            margin: 4px 0;
        ">
            <p style="margin:0; font-size:12px; color:#888; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">{label}</p>
            <p style="margin:4px 0 0 0; font-size:28px; font-weight:800; color:{color};">{value}</p>
            {f'<p style="margin:2px 0 0 0; font-size:12px; color:#888;">{delta}</p>' if delta else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(text: str, color: str = "green"):
    """Render a colored status badge."""
    colors = {
        "green": ("#d4edda", "#155724"),
        "red": ("#f8d7da", "#721c24"),
        "blue": ("#cce5ff", "#004085"),
        "yellow": ("#fff3cd", "#856404"),
        "gray": ("#e2e3e5", "#383d41"),
    }
    bg, fg = colors.get(color, colors["gray"])
    st.markdown(
        f'<span style="background:{bg}; color:{fg}; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600;">{text}</span>',
        unsafe_allow_html=True,
    )


def grade_color(grade: str) -> str:
    """Return color hex for a grade."""
    return {
        "A+": "#1ABC9C", "A": "#2ECC71",
        "B": "#3498DB", "C": "#F39C12",
        "D": "#E67E22", "F": "#E74C3C",
    }.get(grade, "#95A5A6")


def export_session_json() -> str:
    """Export full session results as JSON string."""
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "questions": st.session_state.get("questions", []),
        "students": st.session_state.get("students", []),
        "results": st.session_state.get("evaluation_results", {}),
        "approved_marks": st.session_state.get("approved_marks", {}),
    }
    return json.dumps(export_data, indent=2, ensure_ascii=False)


def format_marks_fraction(obtained: int, maximum: int) -> str:
    """Format marks as 'X / Y'."""
    return f"{obtained} / {maximum}"
