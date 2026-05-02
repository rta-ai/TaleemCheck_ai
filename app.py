"""
TaleemCheck AI – AI-Powered Exam Evaluation & Learning Gap Detection
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import json
import time

# ── Page Config (must be first Streamlit call) ──────────────────────────
st.set_page_config(
    page_title="TaleemCheck AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local Imports ───────────────────────────────────────────────────────
from utils.helpers import (
    init_session_state, reset_all, reset_evaluation,
    metric_card, status_badge, grade_color,
    validate_questions, validate_students, validate_answers,
    get_approved_marks, set_approved_marks,
    apply_approved_marks_to_results, export_session_json,
    format_marks_fraction,
)
from utils.evaluator import (
    get_groq_client, evaluate_answer, extract_text_from_image,
    parse_rubric_document, generate_class_summary, batch_evaluate_student,
)
from utils.parser import (
    extract_text_from_file, get_image_bytes_and_type, parse_manual_answers,
)
from utils.analytics import (
    build_results_dataframe, compute_student_summary,
    get_weak_concepts, get_question_performance, get_analytics_summary,
    chart_student_scores, chart_grade_distribution,
    chart_question_performance, chart_score_distribution,
)
from utils.reports import generate_excel_report, generate_pdf_report

# ── Initialize Session State ─────────────────────────────────────────────
init_session_state()

# ── Global CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #1a2332 100%);
}
[data-testid="stSidebar"] * { color: #e0e6f0 !important; }
[data-testid="stSidebar"] .stRadio label {
    font-size: 14px !important;
    padding: 6px 0 !important;
}

/* ── Main background ── */
.main { background: #f8fafc; }

/* ── Cards ── */
.tc-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04);
    margin-bottom: 16px;
}

/* ── Section headers ── */
.tc-section-header {
    font-size: 22px;
    font-weight: 800;
    color: #0d1117;
    margin-bottom: 4px;
}
.tc-section-sub {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 20px;
}

/* ── Eval result cards ── */
.eval-card {
    background: white;
    border-radius: 10px;
    padding: 20px;
    border-left: 5px solid #3498DB;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 12px;
}
.eval-card.pass { border-left-color: #2ECC71; }
.eval-card.fail { border-left-color: #E74C3C; }

/* ── Tags ── */
.tag {
    display: inline-block;
    background: #EBF5FB;
    color: #2471A3;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 600;
    margin: 2px;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 700 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; }

/* ── Progress bar ── */
.stProgress > div > div { background: linear-gradient(90deg, #2ECC71, #3498DB) !important; }

/* ── Hide Streamlit branding ── */
/* ── Previous Working code with hiding side bar issue hanged with the new below── #MainMenu, footer, header { visibility: hidden; }*/
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
/* ── Home hero ── */
.hero-container {
    background: linear-gradient(135deg, #0d1117 0%, #1a2332 50%, #0d2137 100%);
    border-radius: 16px;
    padding: 60px 40px;
    text-align: center;
    color: white;
    margin-bottom: 30px;
    position: relative;
    overflow: hidden;
}
.hero-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at center, rgba(52,152,219,0.15) 0%, transparent 60%);
}
.hero-title {
    font-size: 48px;
    font-weight: 800;
    margin: 0;
    background: linear-gradient(135deg, #ffffff, #74B9FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 18px;
    color: #94a3b8;
    margin-top: 12px;
}
.hero-badge {
    display: inline-block;
    background: rgba(52,152,219,0.2);
    border: 1px solid rgba(52,152,219,0.4);
    color: #74B9FF;
    border-radius: 20px;
    padding: 4px 16px;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 10px 0;">
        <div style="font-size:36px;">📚</div>
        <div style="font-size:18px; font-weight:800; color:#74B9FF;">TaleemCheck AI</div>
        <div style="font-size:11px; color:#64748b; margin-top:2px;">AI-Powered Exam Evaluation</div>
    </div>
    <hr style="border-color:#2d3748; margin:10px 0 16px 0;">
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        options=["🏠  Home", "📝  Setup & Upload", "🤖  Evaluate", "📊  Results", "📈  Analytics", "⬇️  Export", "⚙️  Settings"],
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border-color:#2d3748; margin:16px 0;'>", unsafe_allow_html=True)

    # API Key input in sidebar
    st.markdown("<p style='font-size:12px; color:#94a3b8; font-weight:600;'>GROQ API KEY</p>", unsafe_allow_html=True)
    api_key_input = st.text_input(
        "API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="gsk_...",
        label_visibility="collapsed",
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    # Status indicator
    if st.session_state.api_key:
        st.markdown('<span style="color:#2ECC71; font-size:12px;">● API Key Set</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="color:#E74C3C; font-size:12px;">● No API Key</span>', unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#2d3748; margin:16px 0;'>", unsafe_allow_html=True)

    # Progress tracker
    st.markdown("<p style='font-size:12px; color:#94a3b8; font-weight:600;'>PROGRESS</p>", unsafe_allow_html=True)
    steps = {
        "API Key": bool(st.session_state.api_key),
        "Questions": bool(st.session_state.questions),
        "Students": bool(st.session_state.students),
        "Answers": bool(st.session_state.student_answers),
        "Evaluated": st.session_state.evaluation_done,
    }
    for step, done in steps.items():
        icon = "✅" if done else "⬜"
        st.markdown(f"<span style='font-size:12px;'>{icon} {step}</span>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# PAGE ROUTER
# ════════════════════════════════════════════════════════════════════════

current_page = page.split("  ")[1].strip() if "  " in page else page


# ════════════════════════════════════════════════════════════════════════
# PAGE 1: HOME
# ════════════════════════════════════════════════════════════════════════

if "Home" in page:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">🇵🇰 Designed for Pakistan's Education Sector</div>
        <h1 class="hero-title">TaleemCheck AI</h1>
        <p class="hero-sub">AI-Assisted Exam Evaluation & Learning Gap Detection System<br>
        Helping teachers evaluate smarter, not harder.</p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="tc-card">
            <div style="font-size:32px; margin-bottom:12px;">🤖</div>
            <div style="font-size:16px; font-weight:700; margin-bottom:8px;">AI-Powered Evaluation</div>
            <div style="font-size:13px; color:#64748b;">Rubric-based answer evaluation using Groq LLaMA 3.3. Fair, consistent, and fast.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="tc-card">
            <div style="font-size:32px; margin-bottom:12px;">✍️</div>
            <div style="font-size:16px; font-weight:700; margin-bottom:8px;">Handwriting Support</div>
            <div style="font-size:13px; color:#64748b;">Upload photos of handwritten answer sheets. AI extracts text using Vision models.</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="tc-card">
            <div style="font-size:32px; margin-bottom:12px;">🌐</div>
            <div style="font-size:16px; font-weight:700; margin-bottom:8px;">Bilingual Feedback</div>
            <div style="font-size:13px; color:#64748b;">Feedback in English and Roman Urdu — making it accessible for all students.</div>
        </div>
        """, unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("""
        <div class="tc-card">
            <div style="font-size:32px; margin-bottom:12px;">📊</div>
            <div style="font-size:16px; font-weight:700; margin-bottom:8px;">Class Analytics</div>
            <div style="font-size:13px; color:#64748b;">Instant charts, grade distribution, weak concept detection, and performance insights.</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown("""
        <div class="tc-card">
            <div style="font-size:32px; margin-bottom:12px;">✏️</div>
            <div style="font-size:16px; font-weight:700; margin-bottom:8px;">Teacher-in-the-Loop</div>
            <div style="font-size:13px; color:#64748b;">AI suggests marks. Teacher reviews, edits, and approves. Full control stays with you.</div>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown("""
        <div class="tc-card">
            <div style="font-size:32px; margin-bottom:12px;">📄</div>
            <div style="font-size:16px; font-weight:700; margin-bottom:8px;">Export Reports</div>
            <div style="font-size:13px; color:#64748b;">Download Excel class reports and individual PDF student reports with one click.</div>
        </div>
        """, unsafe_allow_html=True)

    # How it works
    st.markdown("<div class='tc-section-header' style='margin-top:10px;'>How It Works</div>", unsafe_allow_html=True)
    steps_col = st.columns(5)
    workflow = [
        ("1️⃣", "Add Questions & Rubric"),
        ("2️⃣", "Add Students & Answers"),
        ("3️⃣", "Run AI Evaluation"),
        ("4️⃣", "Review & Approve Marks"),
        ("5️⃣", "Export Reports"),
    ]
    for col, (icon, label) in zip(steps_col, workflow):
        with col:
            st.markdown(f"""
            <div style="text-align:center; padding:16px; background:white; border-radius:10px;
                        box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                <div style="font-size:28px;">{icon}</div>
                <div style="font-size:12px; font-weight:700; margin-top:8px; color:#0d1117;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Get started by entering your **Groq API Key** in the sidebar, then go to **Setup & Upload**.")


# ════════════════════════════════════════════════════════════════════════
# PAGE 2: SETUP & UPLOAD
# ════════════════════════════════════════════════════════════════════════

elif "Setup" in page:
    st.markdown("<div class='tc-section-header'>📝 Setup: Questions & Students</div>", unsafe_allow_html=True)
    st.markdown("<div class='tc-section-sub'>Configure your exam questions, rubric, and student list.</div>", unsafe_allow_html=True)

    # ── SECTION A: Questions & Rubric ────────────────────────────────
    st.markdown("### 📋 Step 1: Questions & Rubric")
    rubric_method = st.radio(
        "How do you want to add questions?",
        ["📤 Upload Question Paper / Rubric File", "✏️ Add Questions Manually"],
        horizontal=True,
    )

    if "Upload" in rubric_method:
        st.markdown("<div class='tc-card'>", unsafe_allow_html=True)
        uploaded_rubric = st.file_uploader(
            "Upload Question Paper with Rubric",
            type=["pdf", "txt", "docx"],
            help="Upload a PDF, TXT, or DOCX file containing questions and marking scheme.",
        )

        if uploaded_rubric:
            with st.spinner("Extracting text from file..."):
                extracted_text = extract_text_from_file(uploaded_rubric)

            if extracted_text.startswith("["):
                st.error(extracted_text)
            else:
                with st.expander("📄 Extracted Text Preview", expanded=False):
                    st.text_area("Extracted Content", extracted_text, height=200, disabled=True)

                if st.button("🤖 Parse Questions with AI", type="primary"):
                    if not st.session_state.api_key:
                        st.error("Please enter your Groq API key in the sidebar first.")
                    else:
                        with st.spinner("AI is parsing your document..."):
                            client = get_groq_client(st.session_state.api_key)
                            questions = parse_rubric_document(client, extracted_text)

                        if questions:
                            st.session_state.questions = questions
                            st.success(f"✅ {len(questions)} questions parsed successfully!")
                            st.rerun()
                        else:
                            st.error("Could not parse questions. Try manual entry instead.")
        st.markdown("</div>", unsafe_allow_html=True)

    else:  # Manual entry
        st.markdown("<div class='tc-card'>", unsafe_allow_html=True)
        num_questions = st.number_input("Number of Questions", min_value=1, max_value=20, value=3)

        manual_questions = []
        for i in range(num_questions):
            st.markdown(f"**Question {i+1}**")
            qcol1, qcol2 = st.columns([3, 1])
            with qcol1:
                q_text = st.text_area(f"Question Text", key=f"q_text_{i}", height=80, label_visibility="collapsed",
                                      placeholder=f"Enter Question {i+1} here...")
            with qcol2:
                q_marks = st.number_input(f"Max Marks", min_value=1, max_value=100, value=5, key=f"q_marks_{i}")

            q_rubric = st.text_area(
                f"Rubric / Expected Points",
                key=f"q_rubric_{i}",
                height=60,
                placeholder="e.g. Must include definition, at least one example, correct terminology...",
            )
            manual_questions.append({
                "question_number": f"Q{i+1}",
                "question": q_text,
                "max_marks": q_marks,
                "rubric": q_rubric if q_rubric else "Award marks based on completeness and accuracy.",
            })
            if i < num_questions - 1:
                st.divider()

        if st.button("💾 Save Questions", type="primary"):
            valid, msg = validate_questions(manual_questions)
            if valid:
                st.session_state.questions = manual_questions
                st.success(f"✅ {len(manual_questions)} questions saved!")
            else:
                st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)

    # Show saved questions summary
    if st.session_state.questions:
        st.markdown("**✅ Saved Questions:**")
        q_preview = pd.DataFrame([
            {"#": q["question_number"], "Question": q["question"][:60]+"...", "Max Marks": q["max_marks"]}
            for q in st.session_state.questions
        ])
        st.dataframe(q_preview, use_container_width=True, hide_index=True)
        total_marks = sum(q["max_marks"] for q in st.session_state.questions)
        st.markdown(f"**Total Exam Marks: {total_marks}**")

    st.divider()

    # ── SECTION B: Students ───────────────────────────────────────────
    st.markdown("### 👥 Step 2: Add Students")
    st.markdown("<div class='tc-card'>", unsafe_allow_html=True)

    students_input = st.text_area(
        "Enter student names (one per line)",
        value="\n".join(st.session_state.students) if st.session_state.students else "",
        height=120,
        placeholder="Ali Hassan\nSara Ahmed\nUsman Khan\nFatima Malik\nZara Nawaz",
    )

    if st.button("💾 Save Students"):
        students = [s.strip() for s in students_input.strip().split("\n") if s.strip()]
        valid, msg = validate_students(students)
        if valid:
            st.session_state.students = students
            # Clear old answers if student list changed
            st.session_state.student_answers = {}
            st.success(f"✅ {len(students)} students saved!")
        else:
            st.error(msg)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.students:
        st.markdown(f"**Students:** {', '.join(st.session_state.students)}")

    st.divider()

    # ── SECTION C: Student Answers ────────────────────────────────────
    if st.session_state.questions and st.session_state.students:
        st.markdown("### 📝 Step 3: Enter Student Answers")

        selected_student = st.selectbox("Select Student", st.session_state.students)

        if selected_student:
            answer_method = st.radio(
                "Answer Input Method",
                ["⌨️ Type / Paste Answers", "📁 Upload Text/PDF File", "📷 Upload Handwritten Image (OCR)"],
                horizontal=True,
                key=f"ans_method_{selected_student}",
            )

            if "Type" in answer_method:
                st.markdown("<div class='tc-card'>", unsafe_allow_html=True)
                st.markdown("*Tip: Label answers as Q1:, Q2:, Q3: or just write them in order.*")
                raw_answers = st.text_area(
                    "Paste all answers here",
                    height=250,
                    key=f"raw_answers_{selected_student}",
                    placeholder="Q1: Artificial Intelligence is...\n\nQ2: Machine learning is a subset of...\n\nQ3: Deep learning uses neural networks...",
                    value="\n\n".join(
                        st.session_state.student_answers.get(selected_student, [])
                    ) if st.session_state.student_answers.get(selected_student) else "",
                )
                if st.button(f"💾 Save Answers for {selected_student}", key=f"save_text_{selected_student}"):
                    parsed = parse_manual_answers(raw_answers, len(st.session_state.questions))
                    st.session_state.student_answers[selected_student] = parsed
                    st.success(f"✅ Answers saved for {selected_student}!")
                st.markdown("</div>", unsafe_allow_html=True)

            elif "Upload" in answer_method and "Image" not in answer_method:
                st.markdown("<div class='tc-card'>", unsafe_allow_html=True)
                uploaded_ans = st.file_uploader(
                    f"Upload answer file for {selected_student}",
                    type=["pdf", "txt", "docx"],
                    key=f"upload_ans_{selected_student}",
                )
                if uploaded_ans:
                    with st.spinner("Extracting text..."):
                        extracted = extract_text_from_file(uploaded_ans)
                    st.text_area("Extracted Text", extracted, height=200, disabled=True)
                    if st.button(f"💾 Parse & Save Answers for {selected_student}", key=f"save_file_{selected_student}"):
                        parsed = parse_manual_answers(extracted, len(st.session_state.questions))
                        st.session_state.student_answers[selected_student] = parsed
                        st.success(f"✅ Answers saved for {selected_student}!")
                st.markdown("</div>", unsafe_allow_html=True)

            elif "Image" in answer_method:
                st.markdown("<div class='tc-card'>", unsafe_allow_html=True)
                st.warning("⚠️ Handwriting OCR is experimental. Works best with clear, neat handwriting.")
                uploaded_img = st.file_uploader(
                    f"Upload handwritten answer sheet image for {selected_student}",
                    type=["png", "jpg", "jpeg"],
                    key=f"upload_img_{selected_student}",
                )
                if uploaded_img:
                    col_img, col_txt = st.columns(2)
                    with col_img:
                        st.image(uploaded_img, caption="Uploaded Image", use_container_width=True)
                    with col_txt:
                        if st.button("🔍 Extract Text with AI Vision", key=f"ocr_{selected_student}", type="primary"):
                            if not st.session_state.api_key:
                                st.error("Please enter your Groq API key first.")
                            else:
                                uploaded_img.seek(0)
                                img_bytes, img_type = get_image_bytes_and_type(uploaded_img)
                                with st.spinner("AI is reading handwriting... this may take a moment."):
                                    client = get_groq_client(st.session_state.api_key)
                                    extracted_text = extract_text_from_image(client, img_bytes, img_type)
                                st.text_area("Extracted Text", extracted_text, height=250, key=f"ocr_result_{selected_student}")
                                parsed = parse_manual_answers(extracted_text, len(st.session_state.questions))
                                st.session_state.student_answers[selected_student] = parsed
                                st.success(f"✅ Text extracted and saved for {selected_student}!")
                st.markdown("</div>", unsafe_allow_html=True)

            # Show saved answers for selected student
            if st.session_state.student_answers.get(selected_student):
                with st.expander(f"👁️ Preview Saved Answers – {selected_student}"):
                    for i, (q, ans) in enumerate(zip(
                        st.session_state.questions,
                        st.session_state.student_answers[selected_student]
                    )):
                        st.markdown(f"**{q['question_number']}:** {ans[:200]}{'...' if len(ans) > 200 else ''}")

        # Overall answers status
        st.markdown("**Answers Status:**")
        ans_status = []
        for s in st.session_state.students:
            has_ans = bool(st.session_state.student_answers.get(s))
            ans_status.append({"Student": s, "Status": "✅ Ready" if has_ans else "❌ Missing"})
        st.dataframe(pd.DataFrame(ans_status), use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════
# PAGE 3: EVALUATE
# ════════════════════════════════════════════════════════════════════════

elif "Evaluat" in page:
    st.markdown("<div class='tc-section-header'>🤖 AI Evaluation Engine</div>", unsafe_allow_html=True)
    st.markdown("<div class='tc-section-sub'>Run AI evaluation for all students. Teacher reviews and approves marks.</div>", unsafe_allow_html=True)

    # Pre-flight checks
    checks = {
        "API Key": bool(st.session_state.api_key),
        "Questions set up": bool(st.session_state.questions),
        "Students added": bool(st.session_state.students),
        "All answers provided": all(
            st.session_state.student_answers.get(s)
            for s in st.session_state.students
        ) if st.session_state.students else False,
    }

    all_good = all(checks.values())

    col_checks, col_action = st.columns([1, 1])
    with col_checks:
        st.markdown("<div class='tc-card'>", unsafe_allow_html=True)
        st.markdown("**Pre-flight Checklist**")
        for check, status in checks.items():
            icon = "✅" if status else "❌"
            st.markdown(f"{icon} {check}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_action:
        st.markdown("<div class='tc-card'>", unsafe_allow_html=True)
        if not all_good:
            st.warning("Complete all setup steps before evaluating.")
        else:
            st.success("All checks passed! Ready to evaluate.")

        model_choice = st.selectbox(
            "AI Model",
            ["llama-3.3-70b-versatile", "llama3-8b-8192", "gemma2-9b-it"],
            index=0,
            help="llama-3.3-70b is recommended for best accuracy.",
        )
        st.session_state.groq_model = model_choice

        if st.button("🚀 Start AI Evaluation", type="primary", disabled=not all_good):
            reset_evaluation()
            client = get_groq_client(st.session_state.api_key)

            total_evals = len(st.session_state.students) * len(st.session_state.questions)
            progress_bar = st.progress(0, text="Starting evaluation...")
            status_placeholder = st.empty()
            completed = [0]

            for student_idx, student in enumerate(st.session_state.students):
                answers = st.session_state.student_answers.get(student, [])
                # Pad answers if needed
                while len(answers) < len(st.session_state.questions):
                    answers.append("")

                student_results = []
                for q_idx, (question, answer) in enumerate(zip(st.session_state.questions, answers)):
                    completed[0] += 1
                    progress = completed[0] / total_evals
                    progress_bar.progress(
                        progress,
                        text=f"Evaluating {student} – {question['question_number']} ({completed[0]}/{total_evals})"
                    )
                    status_placeholder.info(f"🤖 Analyzing: **{student}** | **{question['question_number']}**")

                    result = evaluate_answer(
                        client=client,
                        question=question.get("question", ""),
                        max_marks=question.get("max_marks", 5),
                        rubric=question.get("rubric", ""),
                        student_answer=answer,
                        model=model_choice,
                    )
                    result["question_number"] = question["question_number"]
                    result["question"] = question["question"]
                    result["max_marks"] = question["max_marks"]
                    result["student_name"] = student
                    student_results.append(result)

                    # Small delay to respect rate limits
                    time.sleep(0.3)

                st.session_state.evaluation_results[student] = student_results

            progress_bar.progress(1.0, text="Evaluation complete!")
            status_placeholder.success("✅ All students evaluated successfully!")
            st.session_state.evaluation_done = True
            st.balloons()
            time.sleep(1)
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Results Preview & Mark Editing ───────────────────────────────
    if st.session_state.evaluation_done:
        st.markdown("---")
        st.markdown("### ✏️ Review & Approve Marks")
        st.info("AI has suggested marks below. You can edit any mark before approving. Changes are saved automatically.")

        selected_student = st.selectbox(
            "Select Student to Review",
            st.session_state.students,
            key="review_student_select",
        )

        if selected_student and selected_student in st.session_state.evaluation_results:
            results = st.session_state.evaluation_results[selected_student]
            total_max = sum(r["max_marks"] for r in results)

            # Mark editing table
            approved_marks = {}
            for r in results:
                q_num = r["question_number"]
                ai_marks = r["marks_awarded"]
                max_m = r["max_marks"]

                current_approved = get_approved_marks(selected_student, q_num, ai_marks)

                with st.expander(
                    f"**{q_num}** – AI Suggested: {ai_marks}/{max_m} | {r['question'][:60]}...",
                    expanded=False,
                ):
                    ecol1, ecol2 = st.columns([2, 1])
                    with ecol1:
                        st.markdown(f"**Justification:** {r.get('marks_justification', '')}")
                        if r.get("strengths"):
                            st.markdown("**✅ Strengths:**")
                            for s in r["strengths"]:
                                st.markdown(f"  - {s}")
                        if r.get("missing_concepts"):
                            st.markdown("**❌ Missing Concepts:**")
                            for m in r["missing_concepts"]:
                                st.markdown(f"  - {m}")
                        st.markdown(f"**📝 Feedback (EN):** {r.get('feedback_english', '')}")
                        st.markdown(f"**🗣️ Roman Urdu:** {r.get('feedback_roman_urdu', '')}")
                    with ecol2:
                        new_marks = st.number_input(
                            f"Approved Marks (0–{max_m})",
                            min_value=0,
                            max_value=max_m,
                            value=current_approved,
                            key=f"approve_{selected_student}_{q_num}",
                        )
                        set_approved_marks(selected_student, q_num, new_marks)
                        pct = round(new_marks / max_m * 100)
                        color = "#2ECC71" if pct >= 50 else "#E74C3C"
                        st.markdown(
                            f'<div style="text-align:center; font-size:24px; font-weight:800; color:{color};">{new_marks}/{max_m}</div>',
                            unsafe_allow_html=True,
                        )

            # Student total
            total_approved = sum(
                get_approved_marks(selected_student, r["question_number"], r["marks_awarded"])
                for r in results
            )
            pct = round(total_approved / total_max * 100, 1)
            st.markdown(f"### 🎯 {selected_student}: **{total_approved}/{total_max}** ({pct}%)")


# ════════════════════════════════════════════════════════════════════════
# PAGE 4: RESULTS
# ════════════════════════════════════════════════════════════════════════

elif "Results" in page:
    st.markdown("<div class='tc-section-header'>📊 Evaluation Results</div>", unsafe_allow_html=True)

    if not st.session_state.evaluation_done:
        st.warning("No evaluation results yet. Please run the evaluation first.")
        st.stop()

    # Apply approved marks
    final_results = apply_approved_marks_to_results(
        st.session_state.evaluation_results,
        st.session_state.approved_marks,
    )

    df = build_results_dataframe(final_results)
    student_summary = compute_student_summary(df)
    analytics = get_analytics_summary(df, student_summary)

    # ── Top metrics ───────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    with m1: metric_card("Class Average", f"{analytics['class_average']}%", color="#3498DB")
    with m2: metric_card("Highest Score", f"{analytics['highest_score']}%", color="#2ECC71")
    with m3: metric_card("Pass Rate", f"{analytics['pass_rate']}%", color="#F39C12")
    with m4: metric_card("Class Topper", analytics["topper"], color="#9B59B6")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Leaderboard ───────────────────────────────────────────────────
    st.markdown("### 🏆 Class Leaderboard")
    display_summary = student_summary.copy()

    def color_grade(val):
        colors_map = {
            "A+": "background-color: #d5f5e3; color: #1e8449;",
            "A": "background-color: #d5f5e3; color: #1e8449;",
            "B": "background-color: #d6eaf8; color: #1a5276;",
            "C": "background-color: #fef9e7; color: #9a7d0a;",
            "D": "background-color: #fdebd0; color: #935116;",
            "F": "background-color: #fadbd8; color: #922b21;",
        }
        return colors_map.get(val, "")

    styled = display_summary.style.applymap(color_grade, subset=["Grade"])
    st.dataframe(styled, use_container_width=True)

    # ── Per-student detail cards ──────────────────────────────────────
    st.markdown("### 📋 Detailed Results by Student")

    selected = st.selectbox("Select Student", st.session_state.students, key="results_student")

    if selected and selected in final_results:
        results = final_results[selected]
        total_obtained = sum(r["marks_awarded"] for r in results)
        total_max = sum(r["max_marks"] for r in results)
        pct = round(total_obtained / total_max * 100, 1)
        grade = student_summary[student_summary["Student"] == selected]["Grade"].values
        grade = grade[0] if len(grade) > 0 else "N/A"

        # Student header
        g_color = grade_color(grade)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg, {g_color}22, {g_color}11);
                    border:2px solid {g_color}44; border-radius:12px; padding:20px; margin-bottom:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:22px; font-weight:800;">{selected}</div>
                    <div style="color:#64748b; font-size:14px;">Total: {total_obtained}/{total_max}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:40px; font-weight:800; color:{g_color};">{grade}</div>
                    <div style="font-size:18px; color:{g_color}; font-weight:700;">{pct}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        for r in results:
            marks = r["marks_awarded"]
            max_m = r["max_marks"]
            pct_q = round(marks / max_m * 100)
            card_class = "pass" if pct_q >= 50 else "fail"

            with st.expander(f"{r['question_number']} — {marks}/{max_m} ({pct_q}%)", expanded=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**Question:** {r.get('question', '')}")
                    st.markdown(f"**Justification:** {r.get('marks_justification', '')}")

                    if r.get("strengths"):
                        st.markdown("**✅ Strengths:**")
                        for s in r["strengths"]: st.markdown(f"&nbsp;&nbsp;• {s}")

                    if r.get("missing_concepts"):
                        st.markdown("**❌ Missing Concepts:**")
                        for m in r["missing_concepts"]: st.markdown(f"&nbsp;&nbsp;• {m}")

                    if r.get("improvement_suggestions"):
                        st.markdown("**💡 Improvements:**")
                        for imp in r["improvement_suggestions"]: st.markdown(f"&nbsp;&nbsp;• {imp}")

                    st.markdown(f"**📝 Feedback:** {r.get('feedback_english', '')}")

                    st.markdown(
                        f"<div style='background:#fef9e7; border-radius:8px; padding:8px; margin-top:8px;'>"
                        f"<b>🗣️ Roman Urdu:</b> {r.get('feedback_roman_urdu', '')}</div>",
                        unsafe_allow_html=True,
                    )

                    # Concept tags
                    tags_html = "".join([f'<span class="tag">{t}</span>' for t in r.get("concept_tags", [])])
                    st.markdown(f"<div style='margin-top:8px;'>{tags_html}</div>", unsafe_allow_html=True)

                with c2:
                    bar_color = "#2ECC71" if pct_q >= 50 else "#E74C3C"
                    st.markdown(f"""
                    <div style="text-align:center; padding:16px; background:#f8fafc; border-radius:10px;">
                        <div style="font-size:36px; font-weight:800; color:{bar_color};">{marks}</div>
                        <div style="font-size:14px; color:#64748b;">out of {max_m}</div>
                        <div style="font-size:20px; font-weight:700; color:{bar_color}; margin-top:4px;">{pct_q}%</div>
                        {'<div style="color:#2ECC71; font-size:12px;">✅ Pass</div>' if pct_q >= 50 else '<div style="color:#E74C3C; font-size:12px;">❌ Needs Work</div>'}
                        {'<div style="color:#F39C12; font-size:11px; margin-top:4px;">👨‍🏫 Teacher Approved</div>' if r.get("teacher_approved") else '<div style="color:#94a3b8; font-size:11px; margin-top:4px;">🤖 AI Suggested</div>'}
                    </div>
                    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# PAGE 5: ANALYTICS
# ════════════════════════════════════════════════════════════════════════

elif "Analytics" in page:
    st.markdown("<div class='tc-section-header'>📈 Class Analytics Dashboard</div>", unsafe_allow_html=True)

    if not st.session_state.evaluation_done:
        st.warning("No evaluation data yet. Please run the evaluation first.")
        st.stop()

    final_results = apply_approved_marks_to_results(
        st.session_state.evaluation_results,
        st.session_state.approved_marks,
    )
    df = build_results_dataframe(final_results)
    student_summary = compute_student_summary(df)
    analytics = get_analytics_summary(df, student_summary)
    q_perf = get_question_performance(df)
    weak_concepts = get_weak_concepts(df)

    # ── Key Metrics ───────────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: metric_card("Students", str(analytics["total_students"]), color="#3498DB")
    with m2: metric_card("Class Avg", f"{analytics['class_average']}%", color="#2ECC71")
    with m3: metric_card("Pass Rate", f"{analytics['pass_rate']}%", color="#F39C12")
    with m4: metric_card("Highest", f"{analytics['highest_score']}%", color="#9B59B6")
    with m5: metric_card("Lowest", f"{analytics['lowest_score']}%", color="#E74C3C")

    # ── AI Summary ────────────────────────────────────────────────────
    st.markdown("### 🤖 AI Class Summary")
    with st.spinner("Generating AI summary..."):
        if st.session_state.api_key:
            client = get_groq_client(st.session_state.api_key)
            summary = generate_class_summary(client, analytics)
        else:
            summary = "Enter API key to generate AI class summary."
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, #EBF5FB, #D6EAF8); border-radius:12px;
                padding:20px; border-left:4px solid #3498DB; margin-bottom:20px;">
        <div style="font-size:13px; font-weight:700; color:#1A5276; margin-bottom:8px;">📊 AI ANALYSIS</div>
        <div style="font-size:15px; color:#0d1117; line-height:1.6;">{summary}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Charts Row 1 ──────────────────────────────────────────────────
    ch1, ch2 = st.columns(2)
    with ch1:
        st.plotly_chart(chart_student_scores(student_summary), use_container_width=True)
    with ch2:
        st.plotly_chart(chart_grade_distribution(student_summary), use_container_width=True)

    # ── Charts Row 2 ──────────────────────────────────────────────────
    ch3, ch4 = st.columns(2)
    with ch3:
        st.plotly_chart(chart_question_performance(q_perf), use_container_width=True)
    with ch4:
        st.plotly_chart(chart_score_distribution(student_summary), use_container_width=True)

    # ── Weak Concepts ─────────────────────────────────────────────────
    st.markdown("### ⚠️ Most Common Learning Gaps")
    if weak_concepts:
        wc_df = pd.DataFrame(weak_concepts, columns=["Concept / Gap", "Frequency"])
        st.dataframe(wc_df, use_container_width=True, hide_index=True)
        st.caption("These are the concepts most frequently missing from student answers.")
    else:
        st.info("No learning gaps detected.")

    # ── Question Performance Table ─────────────────────────────────────
    st.markdown("### 📋 Question-wise Performance")
    st.dataframe(q_perf, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════
# PAGE 6: EXPORT
# ════════════════════════════════════════════════════════════════════════

elif "Export" in page:
    st.markdown("<div class='tc-section-header'>⬇️ Export Reports</div>", unsafe_allow_html=True)
    st.markdown("<div class='tc-section-sub'>Download class-wide Excel reports and individual student PDF reports.</div>", unsafe_allow_html=True)

    if not st.session_state.evaluation_done:
        st.warning("No evaluation data yet. Please run the evaluation first.")
        st.stop()

    final_results = apply_approved_marks_to_results(
        st.session_state.evaluation_results,
        st.session_state.approved_marks,
    )
    df = build_results_dataframe(final_results)
    student_summary = compute_student_summary(df)

    col_xl, col_pdf = st.columns(2)

    # ── Excel Export ─────────────────────────────────────────────────
    with col_xl:
        st.markdown("<div class='tc-card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Excel Class Report")
        st.markdown("""
        Includes:
        - Class leaderboard & summary
        - Detailed results for all students
        - Per-student answer breakdown
        - Feedback & improvement notes
        """)
        if st.button("📊 Generate Excel Report", type="primary"):
            with st.spinner("Generating Excel report..."):
                xl_bytes = generate_excel_report(final_results, student_summary, df)
            st.download_button(
                label="⬇️ Download Excel Report",
                data=xl_bytes,
                file_name="TaleemCheck_ClassReport.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── PDF Export ────────────────────────────────────────────────────
    with col_pdf:
        st.markdown("<div class='tc-card'>", unsafe_allow_html=True)
        st.markdown("### 📄 Individual PDF Reports")
        st.markdown("""
        Per student report includes:
        - Marks breakdown per question
        - Strengths and missing concepts
        - English + Roman Urdu feedback
        - Improvement suggestions
        """)
        selected_pdf_student = st.selectbox("Select Student", st.session_state.students, key="pdf_student")

        if st.button("📄 Generate PDF Report", type="primary"):
            if selected_pdf_student in final_results:
                results = final_results[selected_pdf_student]
                total_obt = sum(r["marks_awarded"] for r in results)
                total_max = sum(r["max_marks"] for r in results)

                with st.spinner(f"Generating PDF for {selected_pdf_student}..."):
                    pdf_bytes = generate_pdf_report(selected_pdf_student, results, total_obt, total_max)

                st.download_button(
                    label=f"⬇️ Download {selected_pdf_student}'s Report",
                    data=pdf_bytes,
                    file_name=f"TaleemCheck_{selected_pdf_student.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── JSON Export ───────────────────────────────────────────────────
    st.markdown("### 📦 Raw Data Export")
    col_j1, col_j2 = st.columns(2)
    with col_j1:
        json_data = export_session_json()
        st.download_button(
            label="⬇️ Export Session as JSON",
            data=json_data,
            file_name="TaleemCheck_session.json",
            mime="application/json",
        )
    with col_j2:
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Export Results as CSV",
            data=csv_data,
            file_name="TaleemCheck_results.csv",
            mime="text/csv",
        )


# ════════════════════════════════════════════════════════════════════════
# PAGE 7: SETTINGS / ABOUT
# ════════════════════════════════════════════════════════════════════════

elif "Settings" in page:
    st.markdown("<div class='tc-section-header'>⚙️ Settings & About</div>", unsafe_allow_html=True)

    col_s, col_a = st.columns(2)

    with col_s:
        st.markdown("<div class='tc-card'>", unsafe_allow_html=True)
        st.markdown("### ⚙️ Settings")

        st.markdown("**API Configuration**")
        api_key_settings = st.text_input(
            "Groq API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="gsk_...",
        )
        if api_key_settings:
            st.session_state.api_key = api_key_settings

        st.markdown("**Model Selection**")
        model_settings = st.selectbox(
            "Default AI Model",
            ["llama-3.3-70b-versatile", "llama3-8b-8192", "gemma2-9b-it"],
            index=["llama-3.3-70b-versatile", "llama3-8b-8192", "gemma2-9b-it"].index(
                st.session_state.groq_model
            ),
        )
        st.session_state.groq_model = model_settings

        st.markdown("**Session Management**")
        if st.button("🔄 Reset All Data", type="secondary"):
            reset_all()
            st.success("All data cleared!")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with col_a:
        st.markdown("<div class='tc-card'>", unsafe_allow_html=True)
        st.markdown("### 📚 About TaleemCheck AI")
        st.markdown("""
        **TaleemCheck AI** is an AI-assisted exam evaluation system designed for Pakistan's education sector.

        **Key Features:**
        - 🤖 Groq LLaMA 3.3 powered evaluation
        - ✍️ Handwriting OCR via Groq Vision
        - 🌐 Bilingual feedback (English + Roman Urdu)
        - 📊 Class analytics and learning gap detection
        - ✏️ Teacher review and mark approval
        - 📄 Excel + PDF export

        **Tech Stack:**
        - Frontend: Streamlit
        - LLM: Groq API (LLaMA 3.3 70B)
        - Vision: LLaMA 3.2 Vision
        - Analytics: Pandas + Plotly
        - Export: OpenPyXL + fpdf2

        ---
        *This is an AI-assisted tool. Teachers retain full control over final marks.*

        **Version:** 1.0.0 MVP
        """)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Session State Debug ───────────────────────────────────────────
    with st.expander("🔍 Debug: Session State"):
        debug_info = {
            "api_key_set": bool(st.session_state.api_key),
            "model": st.session_state.groq_model,
            "num_questions": len(st.session_state.questions),
            "num_students": len(st.session_state.students),
            "students_with_answers": len(st.session_state.student_answers),
            "evaluation_done": st.session_state.evaluation_done,
            "num_results": len(st.session_state.evaluation_results),
            "approved_marks_count": sum(
                len(v) for v in st.session_state.approved_marks.values()
            ),
        }
        st.json(debug_info)
