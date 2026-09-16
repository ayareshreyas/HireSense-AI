import re


SKILL_ALIASES = {
    "python": ["python"],
    "java": ["java"],
    "javascript": ["javascript", "js"],
    "sql": ["sql"],

    "machine learning": ["machine learning", "ml"],
    "artificial intelligence": ["artificial intelligence", "ai"],
    "generative ai": ["generative ai", "genai"],
    "deep learning": ["deep learning"],
    "nlp": ["nlp", "natural language processing"],

    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "scikit-learn": ["scikit-learn", "sklearn"],

    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "matplotlib": ["matplotlib"],

    "fastapi": ["fastapi"],
    "flask": ["flask"],
    "django": ["django"],

    "html": ["html"],
    "css": ["css"],
    "react": ["react", "react.js", "reactjs"],
    "node.js": ["node.js", "nodejs"],

    "git": ["git"],
    "github": ["github"],

    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],

    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"]
}


def contains_skill(text, skill):
    text_lower = text.lower()

    for alias in SKILL_ALIASES[skill]:
        pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"

        if re.search(pattern, text_lower):
            return True

    return False


def extract_skills(text):
    found_skills = []

    for skill in SKILL_ALIASES:
        if contains_skill(text, skill):
            found_skills.append(skill)

    return found_skills