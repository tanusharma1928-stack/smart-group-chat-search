import sqlite3
import re
from pathlib import Path

from rank_bm25 import BM25Okapi


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "data" / "chat.db"


# ============================================================
# LOAD MESSAGES
# ============================================================

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


# ============================================================
# TOKENIZATION
# ============================================================

def tokenize(text):

    text = text.lower()

    # Keep English/Hinglish words and numbers
    tokens = re.findall(r"[a-zA-Z0-9]+", text)

    return tokens


# ============================================================
# BUILD BM25 INDEX
# ============================================================

def build_index(messages):

    corpus = [
        tokenize(message["text"])
        for message in messages
    ]

    bm25 = BM25Okapi(corpus)

    return bm25


# ============================================================
# SEARCH
# ============================================================

def search(query, messages, bm25, top_k=10):

    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    scores = bm25.get_scores(query_tokens)

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )

    results = []

    for index in ranked_indices[:top_k]:

        message = messages[index]

        result = {
            "id": message["id"],
            "timestamp": message["timestamp"],
            "sender": message["sender"],
            "text": message["text"],
            "score": float(scores[index]),
            "conversation_id": message["conversation_id"]
        }

        results.append(result)

    return results


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(results):

    print("\n" + "=" * 70)
    print("SEARCH RESULTS")
    print("=" * 70)

    if not results:
        print("No results found.")
        return

    for rank, result in enumerate(results, start=1):

        print(f"\n#{rank}")

        print(f"ID        : {result['id']}")

        print(f"Timestamp : {result['timestamp']}")

        print(f"Sender    : {result['sender']}")

        print(f"Score     : {result['score']:.4f}")

        print(f"Message   : {result['text']}")

        if result["conversation_id"]:
            print(
                f"Thread    : {result['conversation_id']}"
            )

        print("-" * 70)


# ============================================================
# MAIN SEARCH LOOP
# ============================================================

def main():

    print("Loading messages...")

    messages = load_messages()

    print(f"Loaded {len(messages)} messages.")

    print("Building BM25 index...")

    bm25 = build_index(messages)

    print("BM25 index ready.")

    print("\n" + "=" * 70)
    print("SMART GROUP CHAT — BM25 SEARCH")
    print("=" * 70)

    print("\nType your search query.")
    print("Type 'exit' to quit.\n")

    while True:

        query = input("Search: ").strip()

        if query.lower() == "exit":
            print("\nGoodbye!")
            break

        if not query:
            continue

        results = search(
            query,
            messages,
            bm25,
            top_k=10
        )

        display_results(results)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()