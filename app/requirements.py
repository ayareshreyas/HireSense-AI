import re

from app.skills import extract_skills


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
]

PREFERRED_PATTERNS = [
    r"\bpreferred\b",
    r"\bnice to have\b",
    r"\bnice-to-have\b",
    r"\bbonus\b",
    r"\bplus\b",
    r"\badvantage\b",
    r"\bdesirable\b",
]


def split_into_sentences(text):
    """
    Split a job description into smaller requirement statements.
    """

    if not text:
        return []

    text = text.replace("\r", "\n")

    parts = re.split(
        r"(?:\n+|(?<=[.!?])\s+|[•●▪])",
        text
    )

    sentences = []

    for part in parts:
        cleaned = part.strip(" \t-:")

        if cleaned:
            sentences.append(cleaned)

    return sentences


def contains_pattern(text, patterns):
    """
    Check whether text contains one of the supplied patterns.
    """

    text_lower = text.lower()

    for pattern in patterns:
        if re.search(pattern, text_lower):
            return True

    return False


def classify_skill_requirement(skill, sentences):
    """
    Determine whether a skill appears to be required,
    preferred, or unspecified in the job description.
    """

    relevant_sentences = []

    for sentence in sentences:
        sentence_skills = extract_skills(sentence)

        if skill in sentence_skills:
            relevant_sentences.append(sentence)

    for sentence in relevant_sentences:
        if contains_pattern(sentence, PREFERRED_PATTERNS):
            return "preferred"

    for sentence in relevant_sentences:
        if contains_pattern(sentence, REQUIRED_PATTERNS):
            return "required"

    return "unspecified"


def extract_experience_requirements(text):
    """
    Detect explicit years-of-experience requirements
    without returning duplicate matches.
    """

    patterns = [
        r"\bat\s+least\s+\d+\+?\s*(?:years?|yrs?)(?:\s+of\s+experience)?\b",
        r"\bminimum\s+of\s+\d+\+?\s*(?:years?|yrs?)(?:\s+of\s+experience)?\b",
        r"\bminimum\s+\d+\+?\s*(?:years?|yrs?)(?:\s+of\s+experience)?\b",
        r"\b\d+\+?\s*(?:years?|yrs?)\s+of\s+experience\b",
        r"\b\d+\+?\s*(?:years?|yrs?)\s+experience\b",
    ]

    matches = []

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start = match.start()
            end = match.end()

            overlaps_existing = False

            for existing in matches:
                existing_start = existing["start"]
                existing_end = existing["end"]

                if start < existing_end and end > existing_start:
                    overlaps_existing = True

                    current_length = end - start
                    existing_length = existing_end - existing_start

                    if current_length > existing_length:
                        existing["text"] = match.group(0).strip()
                        existing["start"] = start
                        existing["end"] = end

                    break

            if not overlaps_existing:
                matches.append(
                    {
                        "text": match.group(0).strip(),
                        "start": start,
                        "end": end,
                    }
                )

    matches.sort(key=lambda item: item["start"])

    return [item["text"] for item in matches]


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

    for education, aliases in education_keywords.items():
        for alias in aliases:
            if alias in text_lower:
                found.append(education)
                break

    return found


def analyze_job_requirements(job_description):
    """
    Analyze a job description and return structured requirements.
    """

    job_skills = extract_skills(job_description)
    sentences = split_into_sentences(job_description)

    required_skills = []
    preferred_skills = []
    unspecified_skills = []

    for skill in job_skills:
        classification = classify_skill_requirement(
            skill,
            sentences
        )

        if classification == "required":
            required_skills.append(skill)

        elif classification == "preferred":
            preferred_skills.append(skill)

        else:
            unspecified_skills.append(skill)

    return {
        "all_skills": job_skills,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "unspecified_skills": unspecified_skills,
        "experience_requirements":
            extract_experience_requirements(job_description),
        "education_requirements":
            extract_education_requirements(job_description),
    }