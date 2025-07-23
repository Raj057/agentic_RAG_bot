from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

VECTOR_PATH = "vector.index"
CHUNK_PATH = "chunks.npy"

def get_embeddings(chunks):
    return model.encode(chunks)

def save_embeddings(embeddings, chunks):
    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, VECTOR_PATH)
    np.save(CHUNK_PATH, chunks)

def embed_query(query):
    return model.encode([query])[0].astype("float32")

def load_chunks():
    return np.load(CHUNK_PATH, allow_pickle=True)
