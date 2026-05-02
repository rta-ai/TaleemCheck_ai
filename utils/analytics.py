"""
TaleemCheck AI - Analytics Engine
Computes class performance metrics and generates visualizations.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter


def build_results_dataframe(all_results: dict) -> pd.DataFrame:
    """
    Convert raw evaluation results (dict of student -> list of question results)
    into a flat DataFrame for analytics.
    """
    rows = []
    for student_name, question_results in all_results.items():
        for qr in question_results:
            rows.append({
                "Student": student_name,
                "Question": qr.get("question_number", ""),
                "Max Marks": qr.get("max_marks", 0),
                "Marks Awarded": qr.get("marks_awarded", 0),
                "Percentage": round(
                    (qr.get("marks_awarded", 0) / max(qr.get("max_marks", 1), 1)) * 100, 1
                ),
                "Strengths": "; ".join(qr.get("strengths", [])),
                "Missing Concepts": "; ".join(qr.get("missing_concepts", [])),
                "Feedback (EN)": qr.get("feedback_english", ""),
                "Feedback (RU)": qr.get("feedback_roman_urdu", ""),
                "Concept Tags": ", ".join(qr.get("concept_tags", [])),
            })
    return pd.DataFrame(rows)


def compute_student_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-student total marks and percentage."""
    summary = df.groupby("Student").agg(
        Total_Obtained=("Marks Awarded", "sum"),
        Total_Max=("Max Marks", "sum"),
    ).reset_index()
    summary["Percentage"] = (summary["Total_Obtained"] / summary["Total_Max"] * 100).round(1)
    summary["Grade"] = summary["Percentage"].apply(assign_grade)
    summary = summary.sort_values("Percentage", ascending=False).reset_index(drop=True)
    summary.index += 1  # Rank starts at 1
    return summary


def assign_grade(percentage: float) -> str:
    """Assign letter grade based on percentage."""
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "F"


def get_weak_concepts(df: pd.DataFrame, top_n: int = 10) -> list:
    """Extract most commonly missing concepts across all students."""
    all_missing = []
    for val in df["Missing Concepts"].dropna():
        concepts = [c.strip() for c in val.split(";") if c.strip()]
        all_missing.extend(concepts)
    counter = Counter(all_missing)
    return counter.most_common(top_n)


def get_question_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Compute average score per question."""
    return df.groupby("Question").agg(
        Avg_Percentage=("Percentage", "mean"),
        Avg_Marks=("Marks Awarded", "mean"),
        Max_Marks=("Max Marks", "first"),
    ).reset_index().round(1)


def get_analytics_summary(df: pd.DataFrame, student_summary: pd.DataFrame) -> dict:
    """Return key analytics metrics as a dict."""
    return {
        "total_students": student_summary.shape[0],
        "class_average": round(student_summary["Percentage"].mean(), 1),
        "highest_score": student_summary["Percentage"].max(),
        "lowest_score": student_summary["Percentage"].min(),
        "topper": student_summary.iloc[0]["Student"] if not student_summary.empty else "N/A",
        "pass_rate": round(
            (student_summary["Percentage"] >= 50).sum() / max(len(student_summary), 1) * 100, 1
        ),
        "grade_distribution": student_summary["Grade"].value_counts().to_dict(),
    }


# ─────────────────────────────────────────────
# CHART GENERATORS
# ─────────────────────────────────────────────

BRAND_COLORS = ["#2ECC71", "#3498DB", "#E74C3C", "#F39C12", "#9B59B6", "#1ABC9C"]


def chart_student_scores(student_summary: pd.DataFrame):
    """Bar chart of student scores."""
    fig = px.bar(
        student_summary,
        x="Student",
        y="Percentage",
        color="Grade",
        title="Student Score Overview",
        color_discrete_sequence=BRAND_COLORS,
        text="Percentage",
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="Pass Line (50%)")
    fig.update_layout(
        yaxis_range=[0, 110],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI", size=13),
        title_font_size=16,
    )
    return fig


def chart_grade_distribution(student_summary: pd.DataFrame):
    """Pie chart of grade distribution."""
    grade_counts = student_summary["Grade"].value_counts().reset_index()
    grade_counts.columns = ["Grade", "Count"]
    fig = px.pie(
        grade_counts,
        names="Grade",
        values="Count",
        title="Grade Distribution",
        color_discrete_sequence=BRAND_COLORS,
        hole=0.4,
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI", size=13),
    )
    return fig


def chart_question_performance(q_perf: pd.DataFrame):
    """Horizontal bar chart of question average scores."""
    fig = px.bar(
        q_perf.sort_values("Avg_Percentage"),
        x="Avg_Percentage",
        y="Question",
        orientation="h",
        title="Average Score per Question",
        color="Avg_Percentage",
        color_continuous_scale=["#E74C3C", "#F39C12", "#2ECC71"],
        text="Avg_Percentage",
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(
        xaxis_range=[0, 110],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI", size=13),
        coloraxis_showscale=False,
    )
    return fig


def chart_score_distribution(student_summary: pd.DataFrame):
    """Histogram of score distribution."""
    fig = px.histogram(
        student_summary,
        x="Percentage",
        nbins=10,
        title="Score Distribution",
        color_discrete_sequence=["#3498DB"],
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI", size=13),
        bargap=0.1,
    )
    return fig
