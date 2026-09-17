SKILL_DISPLAY_NAMES = {
    "aws": "AWS",
    "gcp": "GCP",
    "nlp": "NLP",
    "sql": "SQL",
    "html": "HTML",
    "css": "CSS",
    "javascript": "JavaScript",
    "node.js": "Node.js",
    "fastapi": "FastAPI",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "scikit-learn": "Scikit-learn",
    "github": "GitHub",
    "artificial intelligence": "Artificial Intelligence",
    "machine learning": "Machine Learning",
    "generative ai": "Generative AI",
}


def format_skill_name(skill):
    return SKILL_DISPLAY_NAMES.get(
        skill,
        skill.title()
    )


def generate_recommendations(
    missing_skills,
    matched_skills,
    skill_evidence,
    job_requirements=None
):
    recommendations = []

    if job_requirements is None:
        job_requirements = {}

    required_skills = job_requirements.get(
        "required_skills",
        []
    )

    preferred_skills = job_requirements.get(
        "preferred_skills",
        []
    )

    unspecified_skills = job_requirements.get(
        "unspecified_skills",
        []
    )

    all_job_skills = (
        required_skills
        + preferred_skills
        + unspecified_skills
    )

    # Handle job descriptions where no supported
    # technical skills were detected.
    if not all_job_skills:
        recommendations.append(
            "No supported technical skills were detected "
            "in this job description, so skill coverage "
            "could not be calculated. Review the job "
            "description manually for requirements that "
            "HireSense does not currently recognize."
        )

        return recommendations

    # 1. Prioritize missing required skills
    for skill in required_skills:
        if skill in missing_skills:
            skill_name = format_skill_name(skill)

            recommendations.append(
                f"{skill_name} is a required skill for this role "
                f"but was not detected in your resume. "
                f"Prioritize gaining or demonstrating relevant "
                f"{skill_name} experience."
            )

    # 2. Handle missing preferred skills separately
    for skill in preferred_skills:
        if skill in missing_skills:
            skill_name = format_skill_name(skill)

            recommendations.append(
                f"{skill_name} is a preferred skill for this role. "
                f"Consider adding evidence of {skill_name} experience "
                f"if you have used it."
            )

    # 3. Handle missing skills that were not classified
    classified_skills = set(
        required_skills + preferred_skills
    )

    for skill in missing_skills:
        if skill not in classified_skills:
            skill_name = format_skill_name(skill)

            recommendations.append(
                f"{skill_name} appears in the job description "
                f"but was not detected in your resume. "
                f"Consider adding evidence of this skill if relevant."
            )

    # 4. Check whether matched skills have project evidence
    for skill in matched_skills:
        sections = skill_evidence.get(
            skill,
            []
        )

        if (
            "Technical Skills" in sections
            and "Projects" not in sections
        ):
            skill_name = format_skill_name(skill)

            recommendations.append(
                f"{skill_name} is listed in your skills, "
                f"but no project evidence was detected. "
                f"Consider demonstrating it through relevant project work."
            )

    # 5. Handle strong skill coverage
    if not recommendations:
        recommendations.append(
            "Your resume demonstrates strong coverage of the "
            "technical skills identified in this job description. "
            "Focus on strengthening your project evidence and "
            "quantifying your achievements."
        )

    return recommendations