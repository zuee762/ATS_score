"""FastAPI Main Application.

Exposes REST APIs for resume parsing, ATS scoring, role-based tailoring,
and PDF/DOCX downloads, plus serves the frontend UI.
"""

from typing import Optional, Dict, Any
import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from backend.job_roles import get_all_roles, get_role_by_id, parse_custom_job_description
from backend.parser import parse_resume_bytes, parse_resume_text
from backend.analyzer import analyze_resume
from backend.optimizer import tailor_resume
from backend.exporter import generate_pdf_bytes, generate_docx_bytes
from backend.samples import SAMPLE_RESUMES

app = FastAPI(
    title="ATS Resume Analyzer & AI Tailor",
    description="Intelligent ATS scoring, gap analysis, and automated resume tailoring engine.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


class TailorRequest(BaseModel):
    parsed_resume: Dict[str, Any]
    target_role_id: str
    custom_jd: Optional[str] = ""
    api_key: Optional[str] = None
    llm_provider: Optional[str] = "local"


class ExportRequest(BaseModel):
    tailored_data: Dict[str, Any]
    format: Optional[str] = "pdf"


@app.get("/api/health")
def health_check():
    return {"status": "online", "service": "ATS Resume Analyzer & Tailor"}


@app.get("/api/roles")
def get_roles():
    """Returns all available job roles."""
    return {"status": "success", "roles": get_all_roles()}


@app.get("/api/samples")
def get_samples():
    """Returns pre-loaded sample resumes."""
    return {"status": "success", "samples": SAMPLE_RESUMES}


@app.post("/api/analyze")
async def analyze_endpoint(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    role_id: str = Form("fullstack_dev"),
    custom_jd: Optional[str] = Form("")
):
    """
    Parses and performs comprehensive ATS analysis on uploaded resume or raw text.
    """
    try:
        if file:
            contents = await file.read()
            parsed = parse_resume_bytes(contents, file.filename or "resume.pdf")
        elif raw_text and raw_text.strip():
            parsed = parse_resume_text(raw_text, "resume.txt")
        else:
            raise HTTPException(status_code=400, detail="Please upload a resume file (PDF/DOCX/TXT) or provide resume text.")

        if not parsed.get("raw_text") or len(parsed["raw_text"].strip()) < 20:
            raise HTTPException(status_code=400, detail="Could not extract readable text from the resume. Please check the file.")

        # Run analysis
        analysis = analyze_resume(parsed, role_id, custom_jd or "")

        # Run initial tailoring
        tailored = tailor_resume(parsed, role_id, custom_jd or "")

        return {
            "status": "success",
            "parsed": parsed,
            "analysis": analysis,
            "tailored": tailored
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/tailor")
def tailor_endpoint(req: TailorRequest):
    """
    Generates customized tailored resume with side-by-side diff.
    """
    try:
        tailored = tailor_resume(
            req.parsed_resume,
            req.target_role_id,
            req.custom_jd or "",
            req.api_key,
            req.llm_provider or "local"
        )
        return {"status": "success", "tailored": tailored}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tailoring failed: {str(e)}")


@app.post("/api/export/pdf")
def export_pdf_endpoint(req: ExportRequest):
    """
    Renders and downloads ATS-compliant PDF resume.
    """
    try:
        pdf_bytes = generate_pdf_bytes(req.tailored_data)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=ATS_Optimized_Resume.pdf"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.post("/api/export/docx")
def export_docx_endpoint(req: ExportRequest):
    """
    Renders and downloads editable Word DOCX resume.
    """
    try:
        docx_bytes = generate_docx_bytes(req.tailored_data)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": "attachment; filename=ATS_Optimized_Resume.docx"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"DOCX generation failed: {str(e)}")


# Serve Frontend Static Files
if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")

    @app.get("/")
    def serve_index():
        return FileResponse(FRONTEND_DIR / "index.html")
