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
}


def format_skill_name(skill):
    return SKILL_DISPLAY_NAMES.get(
        skill,
        skill.title()
    )


def generate_recommendations(
    missing_skills,
    matched_skills,
    skill_evidence
):
    recommendations = []

    # Recommend addressing missing job skills
    for skill in missing_skills:
        skill_name = format_skill_name(skill)

        recommendations.append(
            f"Consider adding evidence of {skill_name} "
            f"experience if you have used it."
        )

    # Check whether matched skills have project evidence
    for skill in matched_skills:
        sections = skill_evidence.get(skill, [])

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

    return recommendations