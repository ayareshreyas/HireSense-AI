import os
import tempfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.matcher import (
    build_analysis,
    calculate_skill_score,
    find_skill_evidence,
    match_skills,
)
from app.parser import clean_text, extract_section, extract_text_from_pdf
from app.recommendations import generate_recommendations
from app.semantic import calculate_semantic_similarity
from app.skills import extract_skills


app = FastAPI(
    title="HireSense AI",
    description="AI-powered resume and job matching API",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "HireSense AI API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    if not resume.filename:
        raise HTTPException(
            status_code=400,
            detail="No resume file provided."
        )

    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are currently supported."
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    temp_path = None

    try:
        # Save uploaded PDF temporarily
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:
            temp_file.write(await resume.read())
            temp_path = temp_file.name

        # Extract and clean resume text
        resume_text = extract_text_from_pdf(temp_path)
        resume_text = clean_text(resume_text)

        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the resume."
            )

        # Extract important resume sections
        professional_summary = extract_section(
            resume_text,
            "PROFESSIONAL SUMMARY",
            [
                "TECHNICAL SKILLS",
                "PROJECTS",
                "EDUCATION",
                "COURSES & TRAINING",
            ],
        )

        technical_skills = extract_section(
            resume_text,
            "TECHNICAL SKILLS",
            [
                "PROJECTS",
                "EDUCATION",
                "COURSES & TRAINING",
            ],
        )

        projects = extract_section(
            resume_text,
            "PROJECTS",
            [
                "EDUCATION",
                "COURSES & TRAINING",
            ],
        )

        resume_sections = {
            "Professional Summary": professional_summary,
            "Technical Skills": technical_skills,
            "Projects": projects,
        }

        # Extract skills
        resume_skills = extract_skills(resume_text)
        job_skills = extract_skills(job_description)

        # Match resume skills against job requirements
        matched_skills, missing_skills = match_skills(
            resume_skills,
            job_skills,
        )

        # Find evidence for matched skills
        skill_evidence = find_skill_evidence(
            matched_skills,
            resume_sections,
        )

        # Calculate skill coverage
        skill_score = calculate_skill_score(
            matched_skills,
            job_skills,
        )

        # Calculate semantic similarity
        semantic_score = calculate_semantic_similarity(
            resume_text,
            job_description,
        )

        # Generate evidence-based recommendations
        recommendations = generate_recommendations(
            missing_skills,
            matched_skills,
            skill_evidence,
        )

        # Build structured analysis
        analysis = build_analysis(
            resume_skills,
            job_skills,
            matched_skills,
            missing_skills,
            skill_evidence,
            skill_score,
            semantic_score,
        )

        # Add recommendations to final response
        analysis["recommendations"] = recommendations

        return analysis

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)