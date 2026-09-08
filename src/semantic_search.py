import sqlite3
import numpy as np
import faiss

from pathlib import Path
from sentence_transformers import SentenceTransformer

# PATHS

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "data" / "chat.db"

MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)

EMBEDDINGS_FILE = MODEL_DIR / "chat_embeddings.npy"

FAISS_INDEX_FILE = MODEL_DIR / "chat.index"

# MODEL

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# LOAD MESSAGES

def load_messages():

    connection = sqlite3.connect(DB_FILE)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            timestamp,
            sender,
            text,
            is_forwarded,
            conversation_id
        FROM messages
        ORDER BY id
    """)

    messages = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return messages

# CREATE EMBEDDINGS

def create_embeddings(messages, model):

    print("\nCreating embeddings...")

    texts = [
        message["text"]
        for message in messages
    ]

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    np.save(
        EMBEDDINGS_FILE,
        embeddings
    )

    print(
        f"\nEmbeddings saved to:\n{EMBEDDINGS_FILE}"
    )

    print(
        f"Embedding shape: {embeddings.shape}"
    )

    return embeddings

# BUILD FAISS INDEX

def build_faiss_index(embeddings):

    print("\nBuilding FAISS index...")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    faiss.write_index(
        index,
        str(FAISS_INDEX_FILE)
    )

    print(
        f"FAISS index saved to:\n{FAISS_INDEX_FILE}"
    )

    print(
        f"Total vectors indexed: {index.ntotal}"
    )

    return index

# SEARCH

def semantic_search(
    query,
    model,
    index,
    messages,
    top_k=10
):

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, index_position in zip(
        scores[0],
        indices[0]
    ):

        if index_position == -1:
            continue

        message = messages[index_position]

        results.append({
            "id": message["id"],
            "timestamp": message["timestamp"],
            "sender": message["sender"],
            "text": message["text"],
            "score": float(score),
            "conversation_id": message["conversation_id"]
        })

    return results

# DISPLAY RESULTS

def display_results(results):

    print("\n" + "=" * 70)
    print("SEMANTIC SEARCH RESULTS")
    print("=" * 70)

    if not results:

        print("No results found.")

        return

    for rank, result in enumerate(
        results,
        start=1
    ):

        print(f"\n#{rank}")

        print(
            f"ID        : {result['id']}"
        )

        print(
            f"Timestamp : {result['timestamp']}"
        )

        print(
            f"Sender    : {result['sender']}"
        )

        print(
            f"Similarity: {result['score']:.4f}"
        )

        print(
            f"Message   : {result['text']}"
        )

        if result["conversation_id"]:

            print(
                f"Thread    : {result['conversation_id']}"
            )

        print("-" * 70)


# MAIN

def main():

    print("=" * 70)
    print("SMART GROUP CHAT — SEMANTIC SEARCH")
    print("=" * 70)

    # Load messages

    print("\nLoading messages...")

    messages = load_messages()

    print(
        f"Loaded {len(messages)} messages."
    )

    # Load model

    print("\nLoading embedding model...")

    print(
        f"Model: {MODEL_NAME}"
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    print("Model loaded successfully.")

    # Create embeddings

    embeddings = create_embeddings(
        messages,
        model
    )

    # Build FAISS

    index = build_faiss_index(
        embeddings
    )

    # Interactive search

    print("\n" + "=" * 70)
    print("SEMANTIC SEARCH READY")
    print("=" * 70)

    print("\nType your query.")

    print("Type 'exit' to quit.\n")

    while True:

        query = input(
            "Search: "
        ).strip()

        if query.lower() == "exit":

            print("\nGoodbye!")

            break

        if not query:

            continue

        results = semantic_search(
            query,
            model,
            index,
            messages,
            top_k=10
        )

        display_results(
            results
        )


# RUN

if __name__ == "__main__":

    main()