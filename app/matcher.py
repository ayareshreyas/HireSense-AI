from app.skills import contains_skill


def match_skills(resume_skills, job_skills):
    """
    Perform literal resume-to-job skill matching.

    These raw results are useful internally for
    evidence detection and recommendation logic.
    """

    matched_skills = []
    missing_skills = []

    for skill in job_skills:
        if skill in resume_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    return matched_skills, missing_skills


def build_requirement_aware_skill_lists(
    resume_skills,
    job_skills,
    alternative_skill_groups=None,
):
    """
    Build user-facing matched and missing skill lists.

    Skills connected by OR are treated as one
    requirement.

    Example:
        TensorFlow OR PyTorch

    If TensorFlow exists in the resume, the
    requirement is satisfied and PyTorch should
    not appear as a missing skill.

    If neither Docker nor Kubernetes exists,
    the missing requirement is displayed as:
        Docker or Kubernetes
    """

    if alternative_skill_groups is None:
        alternative_skill_groups = []

    grouped_skills = set()

    for group in alternative_skill_groups:
        for skill in group.get(
            "skills",
            []
        ):
            grouped_skills.add(skill)

    display_matched_skills = []
    display_missing_skills = []

    # Handle normal independent skills.
    for skill in job_skills:
        if skill in grouped_skills:
            continue

        if skill in resume_skills:
            display_matched_skills.append(
                skill
            )
        else:
            display_missing_skills.append(
                skill
            )

    # Handle OR requirement groups.
    for group in alternative_skill_groups:
        group_skills = group.get(
            "skills",
            []
        )

        if not group_skills:
            continue

        matched_group_skills = [
            skill
            for skill in group_skills
            if skill in resume_skills
        ]

        if matched_group_skills:
            # Show only the skill or skills from the
            # alternative group that the resume has.
            for skill in matched_group_skills:
                if (
                    skill
                    not in display_matched_skills
                ):
                    display_matched_skills.append(
                        skill
                    )

        else:
            # Represent the entire unsatisfied OR
            # requirement as one readable item.
            group_label = " or ".join(
                group_skills
            )

            display_missing_skills.append(
                group_label
            )

    return (
        display_matched_skills,
        display_missing_skills,
    )


def find_skill_evidence(
    matched_skills,
    resume_sections
):
    evidence = {}

    for skill in matched_skills:
        evidence[skill] = []

        for section_name, section_text in (
            resume_sections.items()
        ):
            if contains_skill(
                section_text,
                skill
            ):
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
    alternative_skill_groups=None,
):
    """
    Calculate requirement-aware skill coverage.

    Required skill    = 3 points
    Unspecified skill = 2 points
    Preferred skill   = 1 point

    Skills connected by OR are treated as one
    requirement. Matching any skill in the group
    earns the full weight for that requirement.
    """

    required_weight = 3
    unspecified_weight = 2
    preferred_weight = 1

    if alternative_skill_groups is None:
        alternative_skill_groups = []

    grouped_skills = set()

    for group in alternative_skill_groups:
        for skill in group["skills"]:
            grouped_skills.add(skill)

    independent_required = [
        skill
        for skill in required_skills
        if skill not in grouped_skills
    ]

    independent_preferred = [
        skill
        for skill in preferred_skills
        if skill not in grouped_skills
    ]

    independent_unspecified = [
        skill
        for skill in unspecified_skills
        if skill not in grouped_skills
    ]

    total_possible_score = (
        len(independent_required)
        * required_weight
        + len(independent_unspecified)
        * unspecified_weight
        + len(independent_preferred)
        * preferred_weight
    )

    earned_score = 0

    for skill in independent_required:
        if skill in resume_skills:
            earned_score += required_weight

    for skill in independent_unspecified:
        if skill in resume_skills:
            earned_score += unspecified_weight

    for skill in independent_preferred:
        if skill in resume_skills:
            earned_score += preferred_weight

    for group in alternative_skill_groups:
        requirement_type = group["type"]

        if requirement_type == "required":
            group_weight = required_weight

        elif requirement_type == "preferred":
            group_weight = preferred_weight

        else:
            group_weight = unspecified_weight

        total_possible_score += group_weight

        group_satisfied = any(
            skill in resume_skills
            for skill in group["skills"]
        )

        if group_satisfied:
            earned_score += group_weight

    if total_possible_score == 0:
        return None

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
        return round(
            semantic_score,
            2
        )

    skill_weight = 0.70
    semantic_weight = 0.30

    overall_score = (
        skill_score * skill_weight
        + semantic_score * semantic_weight
    )

    return round(
        overall_score,
        2
    )


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
        "resume_skills":
            resume_skills,

        "job_skills":
            job_skills,

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        "skill_evidence":
            skill_evidence,

        "skill_coverage":
            skill_score,

        "semantic_similarity":
            semantic_score,

        "overall_match_score":
            overall_score,
    }