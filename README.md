# 🎓 TaleemCheck AI

**AI-Powered Exam Evaluation & Learning Gap Detection System**  
*Designed for Pakistan's Education Sector*

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Powered%20by-Groq%20AI-F55036)](https://console.groq.com)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)

---

## 🚀 What is TaleemCheck AI?

TaleemCheck AI is an AI-assisted educational evaluation system that helps teachers:

- ✅ **Reduce manual paper-checking workload**
- 🤖 **Get AI-suggested marks** based on rubric comparison
- 📝 **Generate bilingual feedback** (English + Roman Urdu)
- 📊 **Detect learning gaps** and weak concepts across the class
- 📥 **Export professional reports** (Excel + PDF)
- ✍️ **Extract handwritten answers** using Groq Vision AI

> **Important:** TaleemCheck AI is an AI-*assisted* system. The teacher always reviews and approves final marks. AI suggests — teacher decides.

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 📁 File Upload | PDF, TXT, DOCX answer sheets |
| ✍️ Handwriting OCR | Groq Vision extracts handwritten text from images |
| 🤖 AI Evaluation | Rubric-based grading using LLaMA 3.3-70B |
| 🌐 Bilingual Feedback | English + Roman Urdu for every answer |
| ✏️ Editable Marks | Teacher reviews and edits AI suggestions |
| ✅ Approval Workflow | Teacher approves final grades |
| 📊 Analytics | Charts, grade distribution, learning gaps |
| 📥 Excel Export | Multi-sheet comprehensive class report |
| 📄 PDF Reports | Individual student evaluation reports |

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **LLM:** Groq API (LLaMA 3.3-70B)
- **Vision OCR:** Groq Vision (LLaMA 3.2-11B Vision)
- **PDF Reading:** PyMuPDF (fitz)
- **Data:** Pandas
- **Charts:** Plotly
- **Excel Export:** OpenPyXL
- **PDF Export:** fpdf2

---

## ⚡ Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/taleemcheck-ai.git
cd taleemcheck-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your API key

```bash
cp .env.example .env
# Edit .env and add your Groq API key
```

Or set it directly in the app's Settings page.

### 4. Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 🌐 Deploy on Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app**
4. Select your repo and `app.py`
5. Add secret: `GROQ_API_KEY = "gsk_your_key_here"` in Secrets settings
6. Click **Deploy!**

---

## 📖 How to Use

### Step 1: Settings
- Enter your Groq API key at [console.groq.com](https://console.groq.com) (free)
- Set exam title, subject, class name

### Step 2: Setup & Upload
- Upload question paper (PDF/TXT/DOCX) OR add questions manually
- For each student: upload their answer sheet OR paste answers
- Supports handwritten images (JPG/PNG) via Vision OCR

### Step 3: Evaluate
- Click "Start AI Evaluation"
- AI evaluates each answer against the rubric
- Takes ~3-5 seconds per question per student

### Step 4: Results Dashboard
- Review AI-suggested marks per student
- Edit marks if needed
- Approve evaluations

### Step 5: Analytics
- View class performance charts
- Identify learning gaps
- Generate AI class summary

### Step 6: Reports
- Download Excel report (full class)
- Download individual PDF reports

---

## 📂 Project Structure

```
taleemcheck-ai/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .env.example           # Environment variable template
│
├── utils/
│   ├── __init__.py
│   ├── prompts.py         # LLM prompt templates
│   ├── ocr.py             # File text extraction & Vision OCR
│   ├── parser.py          # Question paper & answer sheet parsing
│   ├── evaluator.py       # AI evaluation engine
│   ├── analytics.py       # Analytics & chart generation
│   ├── reports.py         # Excel & PDF report generation
│   └── helpers.py         # UI helper functions
│
├── .streamlit/
│   └── config.toml        # Streamlit theme configuration
│
└── data/
    ├── sample_question_paper.txt    # Demo question paper
    ├── sample_student_ahmed.txt     # Demo student 1 answers
    └── sample_student_fatima.txt    # Demo student 2 answers
```

---

## 🔑 Getting a Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to **API Keys**
4. Create a new key
5. Copy and paste into TaleemCheck AI Settings

**Free tier** includes generous usage limits — sufficient for hackathon demonstrations.

---

## 📊 Demo Data

Sample files for demo are included in the `data/` folder:

- `data/sample_question_paper.txt` — Computer Science Class 10 exam (6 questions, 30 marks)
- `data/sample_student_ahmed.txt` — Strong student answers
- `data/sample_student_fatima.txt` — Good student answers

---

## 🤝 Hackathon Notes

This project was built for a hackathon focusing on EdTech innovation in Pakistan.

**Positioning:** AI-assisted evaluation system that reduces teacher workload while keeping teacher authority over final grades.

**NOT:** A fully automated system that replaces teachers.

---

## 📄 License

MIT License — Free to use, modify, and distribute.

---

*Built with ❤️ for Pakistan's Education Sector*
