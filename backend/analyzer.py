"""ATS Scoring and Diagnostic Engine.

Calculates multi-dimensional ATS score, identifies key strengths,
critical gaps/weaknesses, missing keywords, and section-by-section improvements.
"""

from typing import Dict, List, Any
import re
from backend.job_roles import JOB_ROLES, parse_custom_job_description


def analyze_resume(parsed_resume: Dict[str, Any], target_role_id: str, custom_jd: str = "") -> Dict[str, Any]:
    """
    Main evaluation pipeline comparing parsed resume against target job role profile or custom JD.
    """
    if custom_jd and custom_jd.strip():
        role_profile = parse_custom_job_description(target_role_id or "Target Role", custom_jd)
    else:
        role_profile = JOB_ROLES.get(target_role_id, JOB_ROLES["fullstack_dev"])

    raw_text = parsed_resume["raw_text"]
    text_lower = raw_text.lower()
    contact = parsed_resume.get("contact", {})
    sections = parsed_resume.get("sections", {})
    
    # 1. Evaluate Skills & Keywords Match (35%)
    skills_eval = evaluate_skills(text_lower, role_profile)
    
    # 2. Evaluate Experience Impact & Action Verbs (30%)
    exp_eval = evaluate_experience(parsed_resume, role_profile)
    
    # 3. Evaluate ATS Readability & Structure (20%)
    format_eval = evaluate_formatting(parsed_resume)
    
    # 4. Evaluate Education & Certifications (15%)
    edu_eval = evaluate_education_and_certs(text_lower, sections, role_profile)
    
    # Weighted Composite Score
    total_score = round(
        (skills_eval["score"] * 0.35) +
        (exp_eval["score"] * 0.30) +
        (format_eval["score"] * 0.20) +
        (edu_eval["score"] * 0.15)
    )
    total_score = max(10, min(99, total_score))
    
    # Grade & Assessment
    if total_score >= 85:
        grade = "A"
        badge_label = "Excellent ATS Match"
        status_color = "emerald"
    elif total_score >= 70:
        grade = "B"
        badge_label = "Strong Match (Minor Gaps)"
        status_color = "blue"
    elif total_score >= 55:
        grade = "C"
        badge_label = "Moderate Match (Needs Optimization)"
        status_color = "amber"
    else:
        grade = "D"
        badge_label = "High ATS Rejection Risk"
        status_color = "rose"

    # Compile Strengths & Weaknesses
    strengths, weaknesses, recommendations = generate_diagnostics(
        skills_eval, exp_eval, format_eval, edu_eval, role_profile, total_score
    )

    # Section-by-section audit
    section_audit = generate_section_audit(parsed_resume, skills_eval, exp_eval, format_eval, edu_eval)

    return {
        "overall_score": total_score,
        "grade": grade,
        "badge_label": badge_label,
        "status_color": status_color,
        "target_role": {
            "id": role_profile["id"],
            "title": role_profile["title"],
            "category": role_profile.get("category", "General"),
            "description": role_profile.get("description", "")
        },
        "score_breakdown": {
            "skills": {
                "score": skills_eval["score"],
                "weight": "35%",
                "label": "Skills & Keywords Match",
                "summary": f"{len(skills_eval['matched_mandatory'])}/{len(role_profile['mandatory_skills'])} Core Skills Found"
            },
            "experience": {
                "score": exp_eval["score"],
                "weight": "30%",
                "label": "Experience & Impact",
                "summary": f"{exp_eval['quantified_ratio']}% Quantified Metrics Found"
            },
            "formatting": {
                "score": format_eval["score"],
                "weight": "20%",
                "label": "ATS Formatting & Structure",
                "summary": f"{format_eval['headers_found']}/5 Key Sections Standardized"
            },
            "education": {
                "score": edu_eval["score"],
                "weight": "15%",
                "label": "Education & Certifications",
                "summary": "Degree & Cert Alignment"
            }
        },
        "keywords_analysis": {
            "matched_mandatory": skills_eval["matched_mandatory"],
            "missing_mandatory": skills_eval["missing_mandatory"],
            "matched_secondary": skills_eval["matched_secondary"],
            "missing_secondary": skills_eval["missing_secondary"],
            "domain_keywords_matched": skills_eval["domain_matched"],
            "domain_keywords_missing": skills_eval["domain_missing"]
        },
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "section_audit": section_audit
    }


def evaluate_skills(text_lower: str, role_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates skill match percentage against target profile."""
    mandatory = role_profile.get("mandatory_skills", [])
    secondary = role_profile.get("secondary_skills", [])
    domain = role_profile.get("domain_keywords", [])
    
    matched_mand = [s for s in mandatory if re.search(r'\b' + re.escape(s.lower()) + r'\b', text_lower)]
    missing_mand = [s for s in mandatory if s not in matched_mand]
    
    matched_sec = [s for s in secondary if re.search(r'\b' + re.escape(s.lower()) + r'\b', text_lower)]
    missing_sec = [s for s in secondary if s not in matched_sec]
    
    matched_dom = [d for d in domain if re.search(r'\b' + re.escape(d.lower()) + r'\b', text_lower)]
    missing_dom = [d for d in domain if d not in matched_dom]
    
    mand_ratio = len(matched_mand) / len(mandatory) if mandatory else 1.0
    sec_ratio = len(matched_sec) / len(secondary) if secondary else 1.0
    dom_ratio = len(matched_dom) / len(domain) if domain else 1.0
    
    score = round((mand_ratio * 60) + (sec_ratio * 25) + (dom_ratio * 15))
    return {
        "score": max(10, min(100, score)),
        "matched_mandatory": matched_mand,
        "missing_mandatory": missing_mand,
        "matched_secondary": matched_sec,
        "missing_secondary": missing_sec,
        "domain_matched": matched_dom,
        "domain_missing": missing_dom
    }


def evaluate_experience(parsed_resume: Dict[str, Any], role_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates the strength of experience bullets, action verbs, and quantifiable metrics."""
    raw_text = parsed_resume["raw_text"]
    exp_items = parsed_resume.get("sections", {}).get("experience", [])
    
    # Gather all bullet points
    all_bullets = []
    if exp_items:
        for item in exp_items:
            all_bullets.extend(item.get("bullets", []))
    else:
        # Fallback to lines
        all_bullets = [l for l in raw_text.split("\n") if len(l.strip()) > 35]

    total_bullets = len(all_bullets) if all_bullets else 1
    
    # Check for quantifiable metrics (percentages, numbers, dollars, stats)
    metric_regex = r'(\d+[\d,.]*\s*%|\$\s*\d+[\d,.]*|\b\d{2,}\b|\b(?:increased|decreased|reduced|grew|scaled|optimized|improved|boosted|saved)\s+by\s+\d+|(\d+x|\d+X))'
    bullets_with_metrics = [b for b in all_bullets if re.search(metric_regex, b)]
    quant_ratio = round((len(bullets_with_metrics) / total_bullets) * 100) if total_bullets else 0
    
    # Check for high-impact action verbs
    preferred_verbs = role_profile.get("action_verbs", []) + [
        "Led", "Architected", "Spearheaded", "Engineered", "Implemented", "Developed",
        "Automated", "Optimized", "Redesigned", "Scaled", "Integrated", "Accelerated",
        "Managed", "Formulated", "Authored", "Standardized", "Reduced", "Increased"
    ]
    
    verbs_found = set()
    for verb in preferred_verbs:
        if re.search(r'\b' + re.escape(verb) + r'\b', raw_text, re.IGNORECASE):
            verbs_found.add(verb)
            
    verb_ratio = min(1.0, len(verbs_found) / 6)
    
    # Experience length / density
    exp_length_score = 100 if len(all_bullets) >= 4 else (len(all_bullets) * 25)
    
    score = round((quant_ratio * 0.40) + (verb_ratio * 100 * 0.35) + (exp_length_score * 0.25))
    return {
        "score": max(15, min(100, score)),
        "bullets_count": len(all_bullets),
        "quantified_count": len(bullets_with_metrics),
        "quantified_ratio": quant_ratio,
        "verbs_found": list(verbs_found)
    }


def evaluate_formatting(parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
    """Assesses ATS readability, word count, contact completeness, and section standards."""
    contact = parsed_resume.get("contact", {})
    raw_sections = parsed_resume.get("sections", {}).get("raw_sections", {})
    word_count = parsed_resume.get("word_count", 0)
    
    # Contact Completeness (max 30 pts)
    contact_score = 0
    if contact.get("name") and contact.get("name") != "Candidate Name":
        contact_score += 8
    if contact.get("email"):
        contact_score += 8
    if contact.get("phone"):
        contact_score += 7
    if contact.get("linkedin") or contact.get("github"):
        contact_score += 7
        
    # Standard Section Headers (max 40 pts)
    standard_keys = ["summary", "experience", "skills", "education", "projects"]
    headers_found = sum(1 for k in standard_keys if k in raw_sections or parsed_resume.get("sections", {}).get(k))
    section_score = (headers_found / len(standard_keys)) * 40
    
    # Word Count Optimization (ideal 400 - 850 words) (max 30 pts)
    if 350 <= word_count <= 950:
        word_score = 30
    elif 200 <= word_count < 350 or 950 < word_count <= 1300:
        word_score = 20
    else:
        word_score = 10
        
    score = round(contact_score + section_score + word_score)
    return {
        "score": max(20, min(100, score)),
        "word_count": word_count,
        "headers_found": headers_found,
        "contact_complete": bool(contact.get("email") and contact.get("phone"))
    }


def evaluate_education_and_certs(text_lower: str, sections: Dict[str, Any], role_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Assesses degree keywords and certification relevance."""
    edu_keywords = role_profile.get("education_keywords", ["Computer Science", "Engineering"])
    certs = role_profile.get("certifications", [])
    
    has_degree = any(bool(re.search(r'\b' + re.escape(deg.lower()) + r'\b', text_lower)) for deg in edu_keywords)
    has_generic_degree = bool(re.search(r'\b(bachelor|master|b\.s\.|m\.s\.|b\.tech|btech|b\.e\.|degree|diploma|phd)\b', text_lower))
    
    matched_certs = [c for c in certs if re.search(r'\b' + re.escape(c.lower()) + r'\b', text_lower)]
    
    score = 50
    if has_degree:
        score += 30
    elif has_generic_degree:
        score += 20
        
    if matched_certs or len(sections.get("certifications", [])) > 0:
        score += 20
        
    return {
        "score": min(100, score),
        "matched_certs": matched_certs,
        "has_relevant_degree": has_degree
    }


def generate_diagnostics(
    skills_eval: Dict[str, Any],
    exp_eval: Dict[str, Any],
    format_eval: Dict[str, Any],
    edu_eval: Dict[str, Any],
    role_profile: Dict[str, Any],
    total_score: int
) -> tuple:
    """Generates structured strengths, weaknesses, and actionable recommendations."""
    strengths = []
    weaknesses = []
    recommendations = []
    
    # Skills diagnostics
    if len(skills_eval["matched_mandatory"]) >= len(role_profile.get("mandatory_skills", [])) * 0.6:
        strengths.append(f"Strong Core Skill Coverage: Successfully detected {len(skills_eval['matched_mandatory'])} critical role keywords ({', '.join(skills_eval['matched_mandatory'][:4])}).")
    else:
        weaknesses.append(f"Missing Core Role Keywords: ATS filters will heavily penalize the absence of essential technologies like {', '.join(skills_eval['missing_mandatory'][:4])}.")
        recommendations.append(f"Add critical missing skills: Prioritize including {', '.join(skills_eval['missing_mandatory'][:3])} into your skills section and bullet points.")
        
    if len(skills_eval["matched_secondary"]) >= 3:
        strengths.append(f"Broad Tooling Ecosystem: Includes relevant frameworks and cloud tools ({', '.join(skills_eval['matched_secondary'][:3])}).")
        
    # Experience diagnostics
    if exp_eval["quantified_ratio"] >= 40:
        strengths.append(f"High-Impact Quantified Results: {exp_eval['quantified_ratio']}% of bullet points contain measurable metrics (%, $, scale).")
    else:
        weaknesses.append("Lack of Quantifiable Metrics: Experience descriptions rely mostly on passive task listings rather than measurable business outcomes.")
        recommendations.append("Apply the XYZ / STAR formula: Rephrase bullet points to highlight 'Accomplished [X], measured by [Y]%, by doing [Z]'.")
        
    if len(exp_eval["verbs_found"]) >= 4:
        strengths.append(f"Dynamic Action Verbs: Strong usage of power verbs such as {', '.join(exp_eval['verbs_found'][:3])}.")
    else:
        recommendations.append("Strengthen Bullet Openers: Replace weak verbs ('Responsible for', 'Assisted with') with commanding action verbs ('Spearheaded', 'Architected', 'Optimized').")
        
    # Formatting diagnostics
    if format_eval["headers_found"] >= 4:
        strengths.append("Standard ATS Hierarchy: Section headings conform to standard Applicant Tracking System parsers.")
    else:
        weaknesses.append("Non-standard Section Headers: Some resume sections might be skipped or miscategorized by automated scrapers.")
        recommendations.append("Standardize Section Titles: Use standard headers like 'Professional Summary', 'Work Experience', 'Technical Skills', 'Education'.")
        
    if format_eval["word_count"] < 350:
        weaknesses.append(f"Brief Resume Length ({format_eval['word_count']} words): Resume may appear sparse. Aim for 450 - 750 words for optimal density.")
    elif format_eval["word_count"] > 1000:
        weaknesses.append(f"Excessive Length ({format_eval['word_count']} words): Long resumes risk parsing truncation in older ATS platforms. Consider streamlining to 1-2 pages.")
        
    return strengths, weaknesses, recommendations


def generate_section_audit(
    parsed_resume: Dict[str, Any],
    skills_eval: Dict[str, Any],
    exp_eval: Dict[str, Any],
    format_eval: Dict[str, Any],
    edu_eval: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Produces detailed section-by-section audit cards."""
    contact = parsed_resume.get("contact", {})
    sections = parsed_resume.get("sections", {})
    
    audit = []
    
    # 1. Header & Contact
    contact_ok = bool(contact.get("email") and contact.get("phone") and (contact.get("linkedin") or contact.get("github")))
    audit.append({
        "section": "Header & Contact Details",
        "score": 95 if contact_ok else 65,
        "status": "pass" if contact_ok else "warning",
        "feedback": "Contact details are complete and parsed cleanly." if contact_ok else "Missing professional links (LinkedIn or GitHub) or contact phone.",
        "tips": "Include Name, Phone, Professional Email, LinkedIn URL, and City/State."
    })
    
    # 2. Professional Summary
    has_summary = bool(sections.get("summary"))
    audit.append({
        "section": "Professional Summary",
        "score": 85 if has_summary else 40,
        "status": "pass" if has_summary else "fail",
        "feedback": "Summary provides a solid 2-3 sentence elevator pitch." if has_summary else "No dedicated Professional Summary detected. A targeted summary significantly boosts ATS relevance.",
        "tips": "Lead with years of experience, core tech stack, and primary career impact."
    })
    
    # 3. Work Experience
    audit.append({
        "section": "Work Experience & Achievements",
        "score": exp_eval["score"],
        "status": "pass" if exp_eval["score"] >= 70 else ("warning" if exp_eval["score"] >= 50 else "fail"),
        "feedback": f"Experience evaluation scored {exp_eval['score']}/100. {exp_eval['quantified_ratio']}% of bullets contain quantified metrics.",
        "tips": "Use bullet points starting with strong action verbs and quantify improvements with numbers, percentages, or cost reductions."
    })
    
    # 4. Technical Skills
    audit.append({
        "section": "Skills & Competencies",
        "score": skills_eval["score"],
        "status": "pass" if skills_eval["score"] >= 70 else ("warning" if skills_eval["score"] >= 50 else "fail"),
        "feedback": f"Matched {len(skills_eval['matched_mandatory'])} core role skills and {len(skills_eval['matched_secondary'])} secondary tools.",
        "tips": f"Add missing keywords: {', '.join(skills_eval['missing_mandatory'][:4])}."
    })
    
    # 5. Education & Credentials
    audit.append({
        "section": "Education & Certifications",
        "score": edu_eval["score"],
        "status": "pass" if edu_eval["score"] >= 70 else "warning",
        "feedback": "Degree information is clearly formatted and aligned." if edu_eval["has_relevant_degree"] else "Degree or specialized industry certifications can be highlighted further.",
        "tips": "List your highest degree, institution, graduation year, and any active relevant certifications."
    })
    
    return audit
