"""Integration test verifying all live HTTP endpoints of the running server."""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    res = requests.get(f"{BASE_URL}/api/health")
    assert res.status_code == 200
    print("[PASS] /api/health responded 200 OK")

def test_static_index():
    res = requests.get(f"{BASE_URL}/")
    assert res.status_code == 200
    assert "ATS" in res.text
    assert "Auto-Tailor" in res.text
    print("[PASS] Static UI served successfully at /")

def test_roles_endpoint():
    res = requests.get(f"{BASE_URL}/api/roles")
    assert res.status_code == 200
    data = res.json()
    assert len(data["roles"]) >= 15
    print(f"[PASS] /api/roles returned {len(data['roles'])} roles")

def test_samples_endpoint():
    res = requests.get(f"{BASE_URL}/api/samples")
    assert res.status_code == 200
    data = res.json()
    assert "junior_frontend" in data["samples"]
    print("[PASS] /api/samples returned sample resumes")

def test_analyze_endpoint():
    samples_res = requests.get(f"{BASE_URL}/api/samples").json()
    sample_text = samples_res["samples"]["junior_frontend"]["content"]
    
    res = requests.post(
        f"{BASE_URL}/api/analyze",
        data={
            "raw_text": sample_text,
            "role_id": "frontend_dev"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "parsed" in data
    assert "analysis" in data
    assert "tailored" in data
    print(f"[PASS] /api/analyze completed (Score: {data['analysis']['overall_score']}%, Projected: {data['tailored']['projected_score']}%)")
    return data

def test_tailor_endpoint(analyze_data):
    res = requests.post(
        f"{BASE_URL}/api/tailor",
        json={
            "parsed_resume": analyze_data["parsed"],
            "target_role_id": "frontend_dev",
            "llm_provider": "local"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["tailored"]["projected_score"] >= 85
    print("[PASS] /api/tailor completed successfully")

def test_pdf_export(analyze_data):
    tailored_data = analyze_data["tailored"]["tailored_data"]
    res = requests.post(
        f"{BASE_URL}/api/export/pdf",
        json={"tailored_data": tailored_data, "format": "pdf"}
    )
    assert res.status_code == 200
    assert res.headers.get("content-type") == "application/pdf"
    assert len(res.content) > 1000
    print(f"[PASS] /api/export/pdf generated valid PDF ({len(res.content)} bytes)")

def test_docx_export(analyze_data):
    tailored_data = analyze_data["tailored"]["tailored_data"]
    res = requests.post(
        f"{BASE_URL}/api/export/docx",
        json={"tailored_data": tailored_data, "format": "docx"}
    )
    assert res.status_code == 200
    assert "document" in res.headers.get("content-type", "")
    assert len(res.content) > 1000
    print(f"[PASS] /api/export/docx generated valid DOCX ({len(res.content)} bytes)")

if __name__ == "__main__":
    test_health()
    test_static_index()
    test_roles_endpoint()
    test_samples_endpoint()
    analyze_data = test_analyze_endpoint()
    test_tailor_endpoint(analyze_data)
    test_pdf_export(analyze_data)
    test_docx_export(analyze_data)
    print("\nALL LIVE SERVER ENDPOINTS VERIFIED AND PASSING 100%!")
