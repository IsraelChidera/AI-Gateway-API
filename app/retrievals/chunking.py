def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")
    if overlap < 0:
        raise ValueError("overlap must be a non-negative integer.")
    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size.")

    text = text.strip()

    if not text:
        return []

    step = chunk_size - overlap
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:       
        end = min(start + chunk_size, text_length)
        chunks.append(text[start:end])
        start += step

    return chunks

if __name__ == "__main__":
    text= "abcdefghijklmnopqrstuvwxyz"
    print(chunk_text(text, chunk_size=14, overlap=3))

article = (
    "You can reset your password from the account settings page. "
    "Go to Settings, then Security, then click Reset Password. "
    "Two-factor authentication can be enabled from security settings. "
    "Invoices are available from the billing dashboard. "
    "Our API uses OAuth 2.0 for authentication."
)

for i, chunk in enumerate(chunk_text(article, chunk_size=50, overlap=10), start=1):
    print(f"Chunk {i}: {chunk}")

# for chunk in chunk_text(article, chunk_size=50, overlap=10):
#     print(f"Chunk: {chunk}")