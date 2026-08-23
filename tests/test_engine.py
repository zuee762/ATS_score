# Unit tests for ATS Engine
from backend.parser import parse_resume_text
from backend.job_roles import get_all_roles, get_role_by_id, parse_custom_job_description
from backend.analyzer import analyze_resume
from backend.optimizer import tailor_resume
from backend.exporter import generate_pdf_bytes, generate_docx_bytes
from backend.samples import SAMPLE_RESUMES

TEST_RESUME = SAMPLE_RESUMES["junior_frontend"]["content"]


def test_job_roles_loaded():
    roles = get_all_roles()
    assert len(roles) >= 15, "Should have at least 15 pre-configured roles"
    fe = get_role_by_id("frontend_dev")
    assert fe is not None
    assert "React" in fe["mandatory_skills"]
    print("[PASS] Job roles test passed")


def test_resume_parser():
    parsed = parse_resume_text(TEST_RESUME, "test_resume.txt")
    assert parsed["contact"]["name"] == "Alex Taylor"
    assert parsed["contact"]["email"] == "alex.taylor.dev@example.com"
    assert parsed["contact"]["phone"] == "(555) 349-2810"
    assert len(parsed["sections"]["skills"]) >= 5
    assert len(parsed["sections"]["experience"]) >= 1
    print("[PASS] Parser test passed")


def test_ats_analyzer():
    parsed = parse_resume_text(TEST_RESUME, "test_resume.txt")
    analysis = analyze_resume(parsed, "frontend_dev")
    
    assert "overall_score" in analysis
    assert 0 <= analysis["overall_score"] <= 100
    assert "score_breakdown" in analysis
    assert len(analysis["strengths"]) > 0
    assert len(analysis["weaknesses"]) > 0
    assert len(analysis["keywords_analysis"]["matched_mandatory"]) > 0
    print(f"[PASS] ATS Analyzer test passed (Overall Score: {analysis['overall_score']})")


def test_custom_jd_parser():
    custom_title = "Senior Cloud Architect"
    custom_desc = "Looking for a Senior Cloud Architect with expertise in AWS, Kubernetes, Terraform, Docker, Python, CI/CD, and Microservices architecture."
    parsed = parse_resume_text(TEST_RESUME, "test_resume.txt")
    analysis = analyze_resume(parsed, custom_title, custom_desc)
    
    assert analysis["target_role"]["title"] == custom_title
    assert "Terraform" in analysis["keywords_analysis"]["missing_mandatory"] or "Terraform" in analysis["keywords_analysis"]["matched_mandatory"]
    print("[PASS] Custom JD Analyzer test passed")


def test_resume_tailoring():
    parsed = parse_resume_text(TEST_RESUME, "test_resume.txt")
    tailored = tailor_resume(parsed, "frontend_dev")
    
    assert tailored["projected_score"] >= 85
    assert len(tailored["tailored_data"]["summary"]) > 50
    assert len(tailored["tailored_data"]["skills"]) >= len(parsed["sections"]["skills"])
    assert len(tailored["tailored_data"]["experience"]) >= 1
    print(f"[PASS] Tailoring test passed (Projected Score: {tailored['projected_score']}%)")


def test_pdf_generation():
    parsed = parse_resume_text(TEST_RESUME, "test_resume.txt")
    tailored = tailor_resume(parsed, "frontend_dev")
    pdf_bytes = generate_pdf_bytes(tailored["tailored_data"])
    
    assert len(pdf_bytes) > 500, "PDF bytes should be non-empty"
    assert pdf_bytes[:4] == b"%PDF", "Must have valid PDF magic bytes header"
    print(f"[PASS] PDF generation test passed ({len(pdf_bytes)} bytes)")


def test_docx_generation():
    parsed = parse_resume_text(TEST_RESUME, "test_resume.txt")
    tailored = tailor_resume(parsed, "frontend_dev")
    docx_bytes = generate_docx_bytes(tailored["tailored_data"])
    
    assert len(docx_bytes) > 500, "DOCX bytes should be non-empty"
    assert docx_bytes[:2] == b"PK", "Must have valid ZIP/DOCX PK magic bytes"
    print(f"[PASS] DOCX generation test passed ({len(docx_bytes)} bytes)")


if __name__ == "__main__":
    test_job_roles_loaded()
    test_resume_parser()
    test_ats_analyzer()
    test_custom_jd_parser()
    test_resume_tailoring()
    test_pdf_generation()
    test_docx_generation()
    print("\nALL 7 CORE TESTS PASSED SUCCESSFULLY!")

