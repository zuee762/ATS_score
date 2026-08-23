# ⚡ ATSForge - AI Resume Analyzer & ATS Optimizer

An advanced, full-stack Applicant Tracking System (ATS) Resume Analyzer and AI-powered Resume Tailor built with a **Python FastAPI** backend and a **modern, glassmorphic dark-mode web frontend**.

---

## ✨ Key Features

1. **Multi-Format Resume Parsing**:
   - Supports **PDF**, **DOCX**, and **TXT** files.
   - Extracts contact information (Email, Phone, LinkedIn, GitHub), professional summaries, work experience, technical skills, projects, and education.

2. **25+ Curated Job Roles & Custom Job Description Support**:
   - Built-in skill taxonomy for roles across Software Engineering, Data & AI, Cloud & DevOps, Cybersecurity, Product Management, UI/UX Design, and QA.
   - **Custom JD Parser**: Paste any custom job description or job posting to dynamically extract required skills, keywords, and qualifications.

3. **Multi-Dimensional ATS Scoring Engine**:
   - **Skills & Keyword Match (35%)**: Mandatory & secondary keyword density and match ratios.
   - **Experience & STAR Impact (30%)**: Power action verbs, quantifiable metrics (`%`, `$`, scale), and bullet structure.
   - **ATS Formatting & Readability (20%)**: Section header standard compliance, word count optimization (400–850 words), and contact completeness.
   - **Education & Certifications (15%)**: Degree relevance and industry certification credentials.

4. **Detailed Diagnostic Reports**:
   - **Identified Strengths**: Highlights what makes the candidate stand out.
   - **Critical Gaps & Weaknesses**: Flags missing must-have keywords and unquantified bullets.
   - **Actionable Recommendations**: Step-by-step checklist to increase ranking.
   - **Section-by-Section Audit**: Line-by-line inspection with tailored improvement tips.

5. **AI Resume Tailoring & Interactive Side-by-Side Editor**:
   - Automatically restructures and rewrites the resume for the target role.
   - Converts weak bullets into high-impact **STAR / XYZ** bullet points (*Accomplished [X], measured by [Y]%, by doing [Z]*).
   - Injects high-priority ATS keywords seamlessly into skills and experience.
   - Side-by-Side Diff View with **Live In-Place Editor** to tweak bullet points or summaries in real time.
   - Shows **Projected ATS Score Boost** (e.g., `66% → 97%`).

6. **One-Click Export**:
   - **Download ATS-Compliant PDF**: Single-column, clean typography, ATS-parser tested via ReportLab.
   - **Download Editable Word (.docx)**: Microsoft Word format via python-docx.
   - **Copy Formatted Text**: Quick clipboard export.

7. **Zero-Setup & Optional Cloud LLM**:
   - Works 100% offline out-of-the-box using built-in NLP & heuristic restructuring.
   - Optional settings modal supports Google Gemini or OpenAI API keys if desired.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python run.py
```
This automatically starts the FastAPI server on `http://127.0.0.1:8000` and opens the web application in your default browser.

---

## 📁 Project Structure

```
f:\ats\
├── backend\
│   ├── __init__.py
│   ├── main.py             # FastAPI endpoints, static file mounting & CORS
│   ├── parser.py           # PDF, DOCX, TXT parser & section segmenter
│   ├── job_roles.py        # 25+ curated roles & custom JD keyword parser
│   ├── analyzer.py         # Multi-dimensional ATS scoring & diagnostics
│   ├── optimizer.py        # AI resume tailor (STAR formula & keyword infusion)
│   ├── exporter.py         # PDF (ReportLab) & DOCX (python-docx) generation
│   └── samples.py          # Pre-built sample resumes for 1-click test drives
├── frontend\
│   ├── index.html          # Semantic single-page application structure
│   ├── css\
│   │   ├── style.css       # Core design system, glassmorphism & dark theme
│   │   ├── components.css  # Gauges, scorecards, diff viewer & modals
│   │   └── animations.css  # Radar scanning, pulses & smooth transitions
│   └── js\
│       ├── app.js          # State management & event orchestration
│       ├── api.js          # REST client for backend endpoints
│       ├── ui.js           # Scorecard renderers & diff viewer
│       └── sample_data.js  # Client fallback sample resumes
├── tests\
│   ├── test_engine.py      # Unit tests for parser, analyzer, optimizer & exporters
│   └── test_api_live.py    # Integration tests for live FastAPI HTTP endpoints
├── requirements.txt        # Python dependencies
└── run.py                  # One-click startup launcher
```
