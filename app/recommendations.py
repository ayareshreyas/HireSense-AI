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


def format_skill_group(skills):
    """
    Convert alternative skills into readable text.

    Examples:
    TensorFlow or PyTorch
    Docker or Kubernetes
    """

    formatted_skills = [
        format_skill_name(skill)
        for skill in skills
    ]

    if len(formatted_skills) == 1:
        return formatted_skills[0]

    if len(formatted_skills) == 2:
        return (
            f"{formatted_skills[0]} "
            f"or {formatted_skills[1]}"
        )

    return (
        ", ".join(formatted_skills[:-1])
        + f", or {formatted_skills[-1]}"
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

    alternative_skill_groups = job_requirements.get(
        "alternative_skill_groups",
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

    # Keep track of every skill that belongs to
    # an alternative requirement group.
    alternative_skills = set()

    for group in alternative_skill_groups:
        group_skills = group.get(
            "skills",
            []
        )

        alternative_skills.update(
            group_skills
        )

    # 1. Handle alternative skill groups.
    #
    # Example:
    # TensorFlow OR PyTorch
    #
    # If TensorFlow is matched, the group is satisfied.
    # PyTorch should therefore NOT be recommended.
    #
    # If neither is matched, recommend the group once.
    for group in alternative_skill_groups:
        group_skills = group.get(
            "skills",
            []
        )

        group_type = group.get(
            "type",
            "unspecified"
        )

        if not group_skills:
            continue

        group_is_satisfied = any(
            skill in matched_skills
            for skill in group_skills
        )

        if group_is_satisfied:
            continue

        group_name = format_skill_group(
            group_skills
        )

        if group_type == "required":
            recommendations.append(
                f"{group_name} is required for this role, "
                f"but none of these alternatives were detected "
                f"in your resume. Prioritize gaining or "
                f"demonstrating experience with at least one "
                f"of these skills."
            )

        elif group_type == "preferred":
            recommendations.append(
                f"{group_name} is preferred for this role. "
                f"Consider adding evidence of experience with "
                f"at least one of these skills if relevant."
            )

        else:
            recommendations.append(
                f"{group_name} appears as an alternative "
                f"requirement in the job description, but none "
                f"of these skills were detected in your resume. "
                f"Consider demonstrating at least one of them "
                f"if relevant."
            )

    # 2. Handle independent missing required skills.
    for skill in required_skills:
        if skill in alternative_skills:
            continue

        if skill in missing_skills:
            skill_name = format_skill_name(
                skill
            )

            recommendations.append(
                f"{skill_name} is a required skill for this role "
                f"but was not detected in your resume. "
                f"Prioritize gaining or demonstrating relevant "
                f"{skill_name} experience."
            )

    # 3. Handle independent missing preferred skills.
    for skill in preferred_skills:
        if skill in alternative_skills:
            continue

        if skill in missing_skills:
            skill_name = format_skill_name(
                skill
            )

            recommendations.append(
                f"{skill_name} is a preferred skill for this role. "
                f"Consider adding evidence of {skill_name} experience "
                f"if you have used it."
            )

    # 4. Handle independent missing unspecified skills.
    classified_skills = set(
        required_skills
        + preferred_skills
    )

    for skill in missing_skills:
        if skill in alternative_skills:
            continue

        if skill not in classified_skills:
            skill_name = format_skill_name(
                skill
            )

            recommendations.append(
                f"{skill_name} appears in the job description "
                f"but was not detected in your resume. "
                f"Consider adding evidence of this skill if relevant."
            )

    # 5. Check whether matched skills have project evidence.
    for skill in matched_skills:
        sections = skill_evidence.get(
            skill,
            []
        )

        if (
            "Technical Skills" in sections
            and "Projects" not in sections
        ):
            skill_name = format_skill_name(
                skill
            )

            recommendations.append(
                f"{skill_name} is listed in your skills, "
                f"but no project evidence was detected. "
                f"Consider demonstrating it through relevant "
                f"project work."
            )

    # 6. Handle strong skill coverage.
    if not recommendations:
        recommendations.append(
            "Your resume demonstrates strong coverage of the "
            "technical skills identified in this job description. "
            "Focus on strengthening your project evidence and "
            "quantifying your achievements."
        )

    return recommendations