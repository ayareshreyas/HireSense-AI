from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


# Load the pretrained embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


sentence1 = "Built machine learning models for classification"

sentence2 = "Experience developing predictive models"


# Convert both sentences into embeddings
embedding1 = model.encode(sentence1)
embedding2 = model.encode(sentence2)


# Compare the meaning of the two sentences
similarity = cos_sim(embedding1, embedding2).item()


print("Sentence 1:")
print(sentence1)

print("\nSentence 2:")
print(sentence2)

print("\nSemantic Similarity:")
print(round(similarity * 100, 2), "%")