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


def find_skill_evidence(
    matched_skills,
    resume_sections
):
    evidence = {}

    for skill in matched_skills:
        evidence[skill] = []

        for section_name, section_text in resume_sections.items():
            if contains_skill(section_text, skill):
                evidence[skill].append(
                    section_name
                )

    return evidence


def calculate_skill_score(
    matched_skills,
    job_skills
):
    """
    Calculate basic unweighted skill coverage.

    Returns None when the job description contains
    no supported technical skills.
    """

    if len(job_skills) == 0:
        return None

    score = (
        len(matched_skills)
        / len(job_skills)
    ) * 100

    return round(score, 2)


def calculate_weighted_skill_score(
    resume_skills,
    required_skills,
    preferred_skills,
    unspecified_skills,
):
    """
    Calculate skill coverage while considering
    the importance of each job requirement.

    Required skill    = 3 points
    Unspecified skill = 2 points
    Preferred skill   = 1 point

    Returns None when no supported technical
    skills were detected in the job description.
    """

    required_weight = 3
    unspecified_weight = 2
    preferred_weight = 1

    total_possible_score = (
        len(required_skills) * required_weight
        + len(unspecified_skills) * unspecified_weight
        + len(preferred_skills) * preferred_weight
    )

    if total_possible_score == 0:
        return None

    earned_score = 0

    for skill in required_skills:
        if skill in resume_skills:
            earned_score += required_weight

    for skill in unspecified_skills:
        if skill in resume_skills:
            earned_score += unspecified_weight

    for skill in preferred_skills:
        if skill in resume_skills:
            earned_score += preferred_weight

    weighted_score = (
        earned_score
        / total_possible_score
    ) * 100

    return round(weighted_score, 2)


def calculate_overall_score(
    skill_score,
    semantic_score
):
    """
    Combine weighted skill coverage and
    semantic similarity.

    When a valid skill score exists:
        Skill coverage      = 70%
        Semantic similarity = 30%

    When no supported job skills were detected,
    semantic similarity becomes the overall score.
    """

    if skill_score is None:
        return round(semantic_score, 2)

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
    overall_score,
):
    return {
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_evidence": skill_evidence,
        "skill_coverage": skill_score,
        "semantic_similarity": semantic_score,
        "overall_match_score": overall_score,
    }