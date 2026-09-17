import re

from app.skills import SKILL_ALIASES, extract_skills


REQUIRED_PATTERNS = [
    r"\brequired\b",
    r"\brequire\b",
    r"\brequires\b",
    r"\brequirements?\b",
    r"\bmust have\b",
    r"\bmust-have\b",
    r"\bshould have\b",
    r"\bstrong knowledge\b",
    r"\bstrong experience\b",
    r"\bproficiency\b",
    r"\bproficient\b",
    r"\bexperience with\b",
    r"\bexperience in\b",

    # Common real-world requirement wording
    r"\bwhat we(?:'re| are) looking for\b",
    r"\bwhat you(?:'ll| will) need\b",
    r"\bwhat you need\b",
    r"\bwe(?:'re| are) looking for\b",
    r"\bwe expect\b",
    r"\byou should know\b",
    r"\bhands-on\b",
    r"\bhands on\b",
    r"\bsolid understanding\b",
    r"\bstrong understanding\b",
    r"\bgood understanding\b",
    r"\bfamiliarity with\b",
    r"\bknowledge of\b",
]


PREFERRED_PATTERNS = [
    r"\bpreferred\b",
    r"\bnice to have\b",
    r"\bnice-to-have\b",
    r"\bbonus\b",
    r"\bplus\b",
    r"\badvantage\b",
    r"\bdesirable\b",

    # Common optional/preferred wording
    r"\bvaluable\b",
    r"\balso valuable\b",
    r"\bhelpful\b",
    r"\bbeneficial\b",
    r"\bwould be useful\b",
    r"\bwould be beneficial\b",
    r"\bwould be a plus\b",
    r"\bis a plus\b",
]


def contains_pattern(text, patterns):
    """
    Check whether text contains one of the
    supplied patterns.
    """

    text_lower = text.lower()

    for pattern in patterns:
        if re.search(pattern, text_lower):
            return True

    return False


def detect_requirement_heading(text):
    """
    Detect whether a line acts as a required
    or preferred skills section heading.

    Examples:
        Required skills:
        Preferred skills:
        Must-have skills:
        Nice-to-have skills:
    """

    cleaned = text.strip().lower()

    cleaned = cleaned.rstrip(":").strip()

    required_headings = [
        "required skills",
        "required skill",
        "requirements",
        "technical requirements",
        "must have skills",
        "must-have skills",
        "must haves",
        "must-haves",
    ]

    preferred_headings = [
        "preferred skills",
        "preferred skill",
        "nice to have skills",
        "nice-to-have skills",
        "nice to haves",
        "nice-to-haves",
        "bonus skills",
        "desired skills",
        "desirable skills",
    ]

    if cleaned in required_headings:
        return "required"

    if cleaned in preferred_headings:
        return "preferred"

    return None


def split_into_sentences(text):
    """
    Split a job description into smaller
    requirement statements while preserving
    required/preferred section context.
    """

    if not text:
        return []

    text = text.replace("\r", "\n")

    raw_parts = re.split(
        r"(?:\n+|(?<=[.!?])\s+|[•●▪])",
        text
    )

    sentences = []

    active_requirement_type = None

    for part in raw_parts:
        cleaned = part.strip(" \t-:")

        if not cleaned:
            continue

        heading_type = detect_requirement_heading(
            part
        )

        if heading_type is not None:
            active_requirement_type = heading_type
            continue

        sentence_skills = extract_skills(
            cleaned
        )

        # If this line contains technical skills and
        # follows a requirement heading, attach the
        # heading context directly to the statement.
        if (
            sentence_skills
            and active_requirement_type
            == "required"
        ):
            cleaned = (
                "Required skills: "
                + cleaned
            )

        elif (
            sentence_skills
            and active_requirement_type
            == "preferred"
        ):
            cleaned = (
                "Preferred skills: "
                + cleaned
            )

        sentences.append(cleaned)

        # Keep the section context while processing
        # skill lines. Reset it once ordinary prose
        # begins so unrelated later sentences are
        # not incorrectly classified.
        if (
            not sentence_skills
            and active_requirement_type
            is not None
        ):
            active_requirement_type = None

    return sentences


def classify_skill_requirement(
    skill,
    sentences
):
    """
    Determine whether a skill appears to be
    required, preferred, or unspecified.
    """

    relevant_sentences = []

    for sentence in sentences:
        sentence_skills = extract_skills(
            sentence
        )

        if skill in sentence_skills:
            relevant_sentences.append(
                sentence
            )

    # Preferred wording takes priority when
    # both kinds of wording appear.
    for sentence in relevant_sentences:
        if contains_pattern(
            sentence,
            PREFERRED_PATTERNS
        ):
            return "preferred"

    for sentence in relevant_sentences:
        if contains_pattern(
            sentence,
            REQUIRED_PATTERNS
        ):
            return "required"

    return "unspecified"


def find_skill_position(
    sentence,
    skill
):
    """
    Find the earliest position of any alias
    belonging to a supported skill.
    """

    aliases = SKILL_ALIASES.get(
        skill,
        [skill]
    )

    earliest_position = None
    earliest_end = None

    for alias in aliases:
        match = re.search(
            r"(?<!\w)"
            + re.escape(alias)
            + r"(?!\w)",
            sentence,
            re.IGNORECASE
        )

        if match:
            if (
                earliest_position is None
                or match.start()
                < earliest_position
            ):
                earliest_position = (
                    match.start()
                )

                earliest_end = (
                    match.end()
                )

    if earliest_position is None:
        return None

    return {
        "start": earliest_position,
        "end": earliest_end,
    }


def extract_alternative_skill_groups(
    sentences
):
    """
    Detect supported technical skills connected
    by the word 'or'.

    Examples:
        TensorFlow or PyTorch
        Docker or Kubernetes

    Each detected group represents one
    requirement that can be satisfied by
    matching any skill in the group.
    """

    alternative_groups = []

    for sentence in sentences:
        sentence_skills = extract_skills(
            sentence
        )

        if len(sentence_skills) < 2:
            continue

        if not re.search(
            r"\bor\b",
            sentence,
            re.IGNORECASE
        ):
            continue

        positioned_skills = []

        for skill in sentence_skills:
            position = find_skill_position(
                sentence,
                skill
            )

            if position is not None:
                positioned_skills.append(
                    {
                        "skill": skill,
                        "start":
                            position["start"],
                        "end":
                            position["end"],
                    }
                )

        positioned_skills.sort(
            key=lambda item: item["start"]
        )

        current_group = []

        for index in range(
            len(positioned_skills) - 1
        ):
            first = positioned_skills[
                index
            ]

            second = positioned_skills[
                index + 1
            ]

            between_text = sentence[
                first["end"]:
                second["start"]
            ]

            if re.search(
                r"\bor\b",
                between_text,
                re.IGNORECASE
            ):
                if (
                    first["skill"]
                    not in current_group
                ):
                    current_group.append(
                        first["skill"]
                    )

                if (
                    second["skill"]
                    not in current_group
                ):
                    current_group.append(
                        second["skill"]
                    )

            else:
                if len(current_group) >= 2:
                    alternative_groups.append(
                        build_alternative_group(
                            current_group,
                            sentence
                        )
                    )

                current_group = []

        if len(current_group) >= 2:
            alternative_groups.append(
                build_alternative_group(
                    current_group,
                    sentence
                )
            )

    unique_groups = []

    for group in alternative_groups:
        if group not in unique_groups:
            unique_groups.append(group)

    return unique_groups


def build_alternative_group(
    skills,
    sentence
):
    """
    Build a structured alternative requirement.
    """

    if contains_pattern(
        sentence,
        PREFERRED_PATTERNS
    ):
        requirement_type = "preferred"

    elif contains_pattern(
        sentence,
        REQUIRED_PATTERNS
    ):
        requirement_type = "required"

    else:
        requirement_type = "unspecified"

    return {
        "skills": skills,
        "type": requirement_type,
    }


def extract_experience_requirements(text):
    """
    Detect explicit years-of-experience
    requirements without duplicates.
    """

    patterns = [
        (
            r"\bat\s+least\s+\d+\+?\s*"
            r"(?:years?|yrs?)"
            r"(?:\s+of\s+experience)?\b"
        ),
        (
            r"\bminimum\s+of\s+\d+\+?\s*"
            r"(?:years?|yrs?)"
            r"(?:\s+of\s+experience)?\b"
        ),
        (
            r"\bminimum\s+\d+\+?\s*"
            r"(?:years?|yrs?)"
            r"(?:\s+of\s+experience)?\b"
        ),
        (
            r"\b\d+\+?\s*(?:years?|yrs?)"
            r"\s+of\s+experience\b"
        ),
        (
            r"\b\d+\+?\s*(?:years?|yrs?)"
            r"\s+experience\b"
        ),
    ]

    matches = []

    for pattern in patterns:
        for match in re.finditer(
            pattern,
            text,
            re.IGNORECASE
        ):
            start = match.start()
            end = match.end()

            overlaps_existing = False

            for existing in matches:
                existing_start = existing[
                    "start"
                ]

                existing_end = existing[
                    "end"
                ]

                if (
                    start < existing_end
                    and end > existing_start
                ):
                    overlaps_existing = True

                    current_length = (
                        end - start
                    )

                    existing_length = (
                        existing_end
                        - existing_start
                    )

                    if (
                        current_length
                        > existing_length
                    ):
                        existing["text"] = (
                            match.group(0).strip()
                        )

                        existing["start"] = start
                        existing["end"] = end

                    break

            if not overlaps_existing:
                matches.append(
                    {
                        "text":
                            match.group(0).strip(),
                        "start":
                            start,
                        "end":
                            end,
                    }
                )

    matches.sort(
        key=lambda item: item["start"]
    )

    return [
        item["text"]
        for item in matches
    ]


def extract_education_requirements(text):
    """
    Detect common education requirements.
    """

    education_keywords = {
        "bachelor's degree": [
            "bachelor's degree",
            "bachelors degree",
            "bachelor degree",
        ],

        "master's degree": [
            "master's degree",
            "masters degree",
            "master degree",
        ],

        "computer science": [
            "computer science",
        ],

        "engineering": [
            "engineering",
        ],
    }

    text_lower = text.lower()

    found = []

    for education, aliases in (
        education_keywords.items()
    ):
        for alias in aliases:
            if alias in text_lower:
                found.append(
                    education
                )
                break

    return found


def analyze_job_requirements(
    job_description
):
    """
    Analyze a job description and return
    structured requirements.
    """

    job_skills = extract_skills(
        job_description
    )

    sentences = split_into_sentences(
        job_description
    )

    required_skills = []
    preferred_skills = []
    unspecified_skills = []

    for skill in job_skills:
        classification = (
            classify_skill_requirement(
                skill,
                sentences
            )
        )

        if classification == "required":
            required_skills.append(
                skill
            )

        elif classification == "preferred":
            preferred_skills.append(
                skill
            )

        else:
            unspecified_skills.append(
                skill
            )

    alternative_skill_groups = (
        extract_alternative_skill_groups(
            sentences
        )
    )

    return {
        "all_skills":
            job_skills,

        "required_skills":
            required_skills,

        "preferred_skills":
            preferred_skills,

        "unspecified_skills":
            unspecified_skills,

        "alternative_skill_groups":
            alternative_skill_groups,

        "experience_requirements":
            extract_experience_requirements(
                job_description
            ),

        "education_requirements":
            extract_education_requirements(
                job_description
            ),
    }