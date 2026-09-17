import os
import tempfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.matcher import (
    build_analysis,
    calculate_overall_score,
    calculate_weighted_skill_score,
    find_skill_evidence,
    match_skills,
)
from app.parser import (
    clean_text,
    extract_section,
    extract_text_from_pdf,
)
from app.recommendations import generate_recommendations
from app.requirements import analyze_job_requirements
from app.semantic import calculate_semantic_similarity
from app.skills import extract_skills


app = FastAPI(
    title="HireSense AI",
    description="AI-powered resume and job matching API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "HireSense AI API is running."
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    if not resume.filename:
        raise HTTPException(
            status_code=400,
            detail="Resume file is required.",
        )

    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are supported.",
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty.",
        )

    temp_path = None

    try:
        file_content = await resume.read()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name

        resume_text = extract_text_from_pdf(
            temp_path
        )

        resume_text = clean_text(
            resume_text
        )

        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="No readable text was found in the resume.",
            )

        cleaned_job_description = clean_text(
            job_description
        )

        # Extract skills from the resume
        resume_skills = extract_skills(
            resume_text
        )

        # Analyze the job description
        job_requirements = analyze_job_requirements(
            cleaned_job_description
        )

        job_skills = job_requirements[
            "all_skills"
        ]

        required_skills = job_requirements[
            "required_skills"
        ]

        preferred_skills = job_requirements[
            "preferred_skills"
        ]

        unspecified_skills = job_requirements[
            "unspecified_skills"
        ]

        # Match resume skills against job skills
        matched_skills, missing_skills = match_skills(
            resume_skills,
            job_skills,
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
            "Professional Summary":
                professional_summary,

            "Technical Skills":
                technical_skills,

            "Projects":
                projects,
        }

        # Find evidence for matched skills
        skill_evidence = find_skill_evidence(
            matched_skills,
            resume_sections,
        )

        # Calculate requirement-aware weighted skill coverage
        skill_score = calculate_weighted_skill_score(
            resume_skills,
            required_skills,
            preferred_skills,
            unspecified_skills,
        )

        # Calculate semantic similarity
        semantic_score = calculate_semantic_similarity(
            resume_text,
            cleaned_job_description,
        )

        # Calculate final overall match score
        overall_score = calculate_overall_score(
            skill_score,
            semantic_score,
        )

        # Build base analysis
        analysis = build_analysis(
            resume_skills,
            job_skills,
            matched_skills,
            missing_skills,
            skill_evidence,
            skill_score,
            semantic_score,
            overall_score,
        )

        # Add structured job requirements
        analysis["job_requirements"] = {
            "required_skills":
                required_skills,

            "preferred_skills":
                preferred_skills,

            "unspecified_skills":
                unspecified_skills,

            "experience_requirements":
                job_requirements[
                    "experience_requirements"
                ],

            "education_requirements":
                job_requirements[
                    "education_requirements"
                ],
        }

        # Generate requirement-aware recommendations
        recommendations = generate_recommendations(
            missing_skills,
            matched_skills,
            skill_evidence,
            job_requirements,
        )

        analysis["recommendations"] = (
            recommendations
        )

        return analysis

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Resume analysis failed: "
                f"{str(error)}"
            ),
        )

    finally:
        if (
            temp_path
            and os.path.exists(temp_path)
        ):
            os.remove(temp_path)