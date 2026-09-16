from app.parser import (
    extract_text_from_pdf,
    read_text_file,
    clean_text,
    extract_section
)

from app.skills import extract_skills

from app.matcher import (
    match_skills,
    find_skill_evidence,
    calculate_skill_score,
    build_analysis
)

from app.semantic import calculate_semantic_similarity


# --------------------------------------------------
# PROCESS RESUME
# --------------------------------------------------

resume_text = extract_text_from_pdf(
    "sample_resumes/sample.pdf"
)

cleaned_resume = clean_text(resume_text)

resume_skills = extract_skills(cleaned_resume)


summary_text = extract_section(
    cleaned_resume,
    "PROFESSIONAL SUMMARY",
    [
        "TECHNICAL SKILLS",
        "PROJECTS",
        "EDUCATION",
        "COURSES & TRAINING"
    ]
)

skills_text = extract_section(
    cleaned_resume,
    "TECHNICAL SKILLS",
    [
        "PROJECTS",
        "EDUCATION",
        "COURSES & TRAINING"
    ]
)

projects_text = extract_section(
    cleaned_resume,
    "PROJECTS",
    [
        "EDUCATION",
        "COURSES & TRAINING"
    ]
)


resume_sections = {
    "Professional Summary": summary_text,
    "Technical Skills": skills_text,
    "Projects": projects_text
}


# --------------------------------------------------
# PROCESS JOB DESCRIPTION
# --------------------------------------------------

job_text = read_text_file(
    "sample_jobs/job_description.txt"
)

cleaned_job = clean_text(job_text)

job_skills = extract_skills(cleaned_job)


# --------------------------------------------------
# MATCHING
# --------------------------------------------------

matched_skills, missing_skills = match_skills(
    resume_skills,
    job_skills
)

skill_evidence = find_skill_evidence(
    matched_skills,
    resume_sections
)

skill_score = calculate_skill_score(
    matched_skills,
    job_skills
)

semantic_score = calculate_semantic_similarity(
    cleaned_resume,
    cleaned_job
)


analysis = build_analysis(
    resume_skills,
    job_skills,
    matched_skills,
    missing_skills,
    skill_evidence,
    skill_score,
    semantic_score
)


# --------------------------------------------------
# OUTPUT
# --------------------------------------------------

print("\n========== HireSense Analysis ==========")

print("\nRequired Skill Coverage:")
print(f"{analysis['skill_coverage']}%")


print("\nSemantic Similarity:")
print(f"{analysis['semantic_similarity']}%")


print("\nMatched Skills:")

for skill in analysis["matched_skills"]:
    print("-", skill)


print("\nMissing Skills:")

for skill in analysis["missing_skills"]:
    print("-", skill)


print("\nSkill Evidence:")

for skill, sections in analysis["skill_evidence"].items():
    print(f"\n{skill}:")

    if sections:
        for section in sections:
            print(f"  - {section}")
    else:
        print("  - No section evidence found")


print("\nDetected Resume Skills:")

for skill in analysis["resume_skills"]:
    print("-", skill)


print("\n========================================")