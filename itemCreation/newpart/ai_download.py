from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
model.save("local_model")

# In your browser:
# Go here:https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
# Click: “Download” → download all files