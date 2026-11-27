"""Worked example: a minimal RAG in about 20 lines (index, retrieve, augment, generate)."""
import numpy as np

from _common import EMBEDDING_MODEL, MODEL, get_client

client = get_client()

docs = ["Refunds for cancelled orders take 5-7 working days.",
        "UPI refunds are usually faster: 1-3 working days.",
        "Delivery partners can't accept cash above ₹2,000."]

def embed(texts):
    out = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return np.array([d.embedding for d in out.data])

doc_vecs = embed(docs)                                 # 1. index once
question = "I paid by UPI, when will my refund come?"
q_vec = embed([question])[0]                           # 2. embed the question
scores = doc_vecs @ q_vec                              # 3. similarity (vectors are normalised)
top = [docs[i] for i in scores.argsort()[::-1][:2]]   # 4. best 2 chunks
print("Retrieved:", top)

answer = client.chat.completions.create(model=MODEL, messages=[
    {"role": "system", "content": "Answer only from this context:\n" + "\n".join(top)},
    {"role": "user", "content": question}])           # 5. augment + generate
print(answer.choices[0].message.content)
