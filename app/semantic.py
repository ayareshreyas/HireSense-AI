from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_semantic_similarity(resume_text, job_text):
    if not resume_text or not job_text:
        return 0

    embeddings = model.encode(
        [resume_text, job_text],
        convert_to_tensor=True
    )

    similarity = cos_sim(
        embeddings[0],
        embeddings[1]
    ).item()

    return round(similarity * 100, 2)