import math

from app.retrievals.embeddings import documents, embed_documents, embed_query

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Score from about -1 to 1. Higher means more similar in meaning."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)


def search(query: str, documents: list[str], k: int = 3) -> list[tuple[str, float]]:
    # 1. Embed the documents and the query
    doc_vectors = embed_documents(documents)
    query_vector = embed_query(query)

    # 2. Compare the query against every document vector
    scored = []
    for doc, doc_vector in zip(documents, doc_vectors):
        score = cosine_similarity(query_vector, doc_vector)
        scored.append((doc, score))

    # 3. Rank: highest score first
    scored.sort(key=lambda pair: pair[1], reverse=True)

    # 4. Return the top k
    return scored[:k]


if __name__ == "__main__":
    query = "Where can I change my password?"
    results = search(query, documents, k=3)

    print(f"Query: {query}\n")
    for rank, (doc, score) in enumerate(results, start=1):
        print(f"{rank}. ({score:.3f}) {doc}")
