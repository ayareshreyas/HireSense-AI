from app.skills import contains_skill


def match_skills(resume_skills, job_skills):
    matched_skills = []
    missing_skills = []

    for skill in job_skills:
        if skill in resume_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    return matched_skills, missing_skills


def find_skill_evidence(matched_skills, resume_sections):
    evidence = {}

    for skill in matched_skills:
        evidence[skill] = []

        for section_name, section_text in resume_sections.items():
            if contains_skill(section_text, skill):
                evidence[skill].append(section_name)

    return evidence


def calculate_skill_score(matched_skills, job_skills):
    if len(job_skills) == 0:
        return 0

    score = (
        len(matched_skills) /
        len(job_skills)
    ) * 100

    return round(score, 2)


def calculate_overall_score(skill_score, semantic_score):
    skill_weight = 0.70
    semantic_weight = 0.30

    overall_score = (
        skill_score * skill_weight
        + semantic_score * semantic_weight
    )

    return round(overall_score, 2)


def build_analysis(
    resume_skills,
    job_skills,
    matched_skills,
    missing_skills,
    skill_evidence,
    skill_score,
    semantic_score,
    overall_score
):
    return {
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_evidence": skill_evidence,
        "skill_coverage": skill_score,
        "semantic_similarity": semantic_score,
        "overall_match_score": overall_score
    }