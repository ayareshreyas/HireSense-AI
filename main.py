import re
import pymupdf

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


# Load semantic embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Skills and their common aliases
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


# Extract text from a PDF resume
def extract_text_from_pdf(pdf_path):
    document = pymupdf.open(pdf_path)
    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text


# Read text from a job description file
def read_text_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# Clean unnecessary spaces and blank lines
def clean_text(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip()


# Find known technical skills and normalize aliases
def extract_skills(text):
    found_skills = []
    text_lower = text.lower()

    for skill, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"

            if re.search(pattern, text_lower):
                found_skills.append(skill)
                break

    return found_skills


# Compare resume skills with job requirements
def match_skills(resume_skills, job_skills):
    matched_skills = []
    missing_skills = []

    for skill in job_skills:
        if skill in resume_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    return matched_skills, missing_skills


# Calculate skill match percentage
def calculate_skill_score(matched_skills, job_skills):
    if len(job_skills) == 0:
        return 0

    score = (len(matched_skills) / len(job_skills)) * 100

    return round(score, 2)


# Calculate semantic similarity between resume and job description
def calculate_semantic_similarity(resume_text, job_text):
    embeddings = model.encode(
        [resume_text, job_text],
        convert_to_tensor=True
    )

    similarity = cos_sim(
        embeddings[0],
        embeddings[1]
    ).item()

    return round(similarity * 100, 2)


# Process resume
resume_text = extract_text_from_pdf(
    "sample_resumes/sample.pdf"
)
cleaned_resume = clean_text(resume_text)
resume_skills = extract_skills(cleaned_resume)


# Process job description
job_text = read_text_file(
    "sample_jobs/job_description.txt"
)
cleaned_job = clean_text(job_text)
job_skills = extract_skills(cleaned_job)


# Compare resume and job skills
matched_skills, missing_skills = match_skills(
    resume_skills,
    job_skills
)

skill_score = calculate_skill_score(
    matched_skills,
    job_skills
)


# Calculate semantic similarity
semantic_score = calculate_semantic_similarity(
    cleaned_resume,
    cleaned_job
)


# Display results
print("\nResume Skills:")

for skill in resume_skills:
    print("-", skill)


print("\nJob Required Skills:")

for skill in job_skills:
    print("-", skill)


print("\nMatched Skills:")

for skill in matched_skills:
    print("-", skill)


print("\nMissing Skills:")

for skill in missing_skills:
    print("-", skill)


print(f"\nSkill Match Score: {skill_score}%")
print(f"Semantic Similarity Score: {semantic_score}%")