import sqlite3
import re
import numpy as np
import faiss

from pathlib import Path
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from query_analyzer import analyze_query


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "data" / "chat.db"
FAISS_INDEX_FILE = BASE_DIR / "models" / "chat.index"


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


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
# TOKENIZER
# ============================================================

def tokenize(text):

    text = text.lower()

    return re.findall(r"[a-zA-Z0-9]+", text)


# ============================================================
# BUILD BM25
# ============================================================

def build_bm25(messages):

    corpus = [
        tokenize(message["text"])
        for message in messages
    ]

    return BM25Okapi(corpus)


# ============================================================
# NORMALIZE SCORES
# ============================================================

def normalize_scores(scores):

    scores = np.asarray(scores, dtype=float)

    if len(scores) == 0:
        return scores

    minimum = scores.min()
    maximum = scores.max()

    if maximum == minimum:
        return np.ones(len(scores))

    return (scores - minimum) / (maximum - minimum)


# ============================================================
# CLEAN QUERY
# ============================================================

def clean_query(query, query_info):

    cleaned = query

    # Remove person's name from attributed queries
    if query_info["person"]:

        cleaned = re.sub(
            r"\b" + re.escape(query_info["person"]) + r"\b",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

    # Remove common question words
    stop_phrases = [
        "what did",
        "what was",
        "what were",
        "what do",
        "what does",
        "tell me",
        "show me",
        "when did",
        "when was",
        "when were",
        "who said",
        "say about",
        "discuss",
        "we discuss",
        "last month",
        "previous month",
        "this month",
        "last week",
    ]

    for phrase in stop_phrases:
        cleaned = re.sub(
            r"\b" + re.escape(phrase) + r"\b",
            " ",
            cleaned,
            flags=re.IGNORECASE
        )

    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned if cleaned else query


# ============================================================
# CHECK DATE RANGE
# ============================================================

def inside_date_range(message, start_date, end_date):

    if not start_date or not end_date:
        return True

    timestamp = message["timestamp"]

    return start_date <= timestamp < end_date


# ============================================================
# DECISION INTENT BOOST
# ============================================================

def decision_boost(query, text):

    query_lower = query.lower()
    text_lower = text.lower()

    decision_words = [
        "decide",
        "decided",
        "decision",
        "final",
        "fix",
        "fixed",
        "locked",
        "confirm",
        "confirmed",
        "finalize",
        "finalised",
        "done then",
        "lock kar",
        "fix hai",
        "pakka"
    ]

    query_is_decision = any(
        word in query_lower
        for word in decision_words
    )

    if not query_is_decision:
        return 0.0

    if any(
        word in text_lower
        for word in decision_words
    ):
        return 0.20

    return 0.0


# ============================================================
# HYBRID SEARCH
# ============================================================

def hybrid_search(
    query,
    messages,
    bm25,
    model,
    faiss_index,
    top_k=10
):

    # --------------------------------------------------------
    # 1. ANALYZE QUERY
    # --------------------------------------------------------

    query_info = analyze_query(query)

    query_type = query_info["type"]

    person = query_info["person"]

    start_date = query_info["start_date"]

    end_date = query_info["end_date"]

    search_query = clean_query(
        query,
        query_info
    )

    # --------------------------------------------------------
    # 2. BM25 SEARCH
    # --------------------------------------------------------

    query_tokens = tokenize(search_query)

    bm25_scores = bm25.get_scores(query_tokens)

    normalized_bm25 = normalize_scores(
        bm25_scores
    )

    # --------------------------------------------------------
    # 3. SEMANTIC SEARCH
    # --------------------------------------------------------

    query_embedding = model.encode(
        [search_query],
        normalize_embeddings=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    semantic_scores, semantic_indices = faiss_index.search(
        query_embedding,
        len(messages)
    )

    semantic_scores = semantic_scores[0]
    semantic_indices = semantic_indices[0]

    normalized_semantic = normalize_scores(
        semantic_scores
    )

    semantic_map = {}

    for position, message_index in enumerate(
        semantic_indices
    ):

        if message_index == -1:
            continue

        semantic_map[int(message_index)] = (
            normalized_semantic[position]
        )

    # --------------------------------------------------------
    # 4. FILTER + HYBRID SCORE
    # --------------------------------------------------------

    results = []

    for index, message in enumerate(messages):

        # ----------------------------------------------------
        # ATTRIBUTED FILTER
        # ----------------------------------------------------

        if query_type == "attributed":

            if person and message["sender"].lower() != person.lower():
                continue

        # ----------------------------------------------------
        # TEMPORAL FILTER
        # ----------------------------------------------------

        if query_type == "temporal":

            if not inside_date_range(
                message,
                start_date,
                end_date
            ):
                continue

        # ----------------------------------------------------
        # SCORES
        # ----------------------------------------------------

        semantic_score = semantic_map.get(
            index,
            0.0
        )

        bm25_score = normalized_bm25[index]

        hybrid_score = (
            0.5 * bm25_score
            +
            0.5 * semantic_score
        )

        # ----------------------------------------------------
        # DECISION BOOST
        # ----------------------------------------------------

        hybrid_score += decision_boost(
            query,
            message["text"]
        )

        results.append({

            "id": message["id"],

            "timestamp": message["timestamp"],

            "sender": message["sender"],

            "text": message["text"],

            "conversation_id":
                message["conversation_id"],

            "bm25_score":
                float(bm25_score),

            "semantic_score":
                float(semantic_score),

            "hybrid_score":
                float(hybrid_score)

        })

    # --------------------------------------------------------
    # 5. SORT
    # --------------------------------------------------------

    results.sort(
        key=lambda x: x["hybrid_score"],
        reverse=True
    )

    return results[:top_k]


# ============================================================
# GET CONTEXT
# ============================================================

def get_context(
    messages,
    result,
    context_size=5
):

    target_id = result["id"]

    target_index = None

    for i, message in enumerate(messages):

        if message["id"] == target_id:

            target_index = i
            break

    if target_index is None:
        return []

    start = max(
        0,
        target_index - context_size
    )

    end = min(
        len(messages),
        target_index + context_size + 1
    )

    return messages[start:end]


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(
    results,
    messages,
    query_info
):

    print("\n")
    print("=" * 80)
    print("HYBRID SEARCH RESULTS")
    print("=" * 80)

    print(
        f"Query Type : {query_info['type']}"
    )

    if query_info["person"]:

        print(
            f"Person     : {query_info['person']}"
        )

    if query_info["start_date"]:

        print(
            f"Date Range : "
            f"{query_info['start_date']} "
            f"to "
            f"{query_info['end_date']}"
        )

    print("=" * 80)

    if not results:

        print("No results found.")
        return

    for rank, result in enumerate(
        results,
        start=1
    ):

        print(f"\n#{rank}")

        print(
            f"ID              : {result['id']}"
        )

        print(
            f"Timestamp       : {result['timestamp']}"
        )

        print(
            f"Sender          : {result['sender']}"
        )

        print(
            f"BM25 Score      : "
            f"{result['bm25_score']:.4f}"
        )

        print(
            f"Semantic Score  : "
            f"{result['semantic_score']:.4f}"
        )

        print(
            f"Hybrid Score    : "
            f"{result['hybrid_score']:.4f}"
        )

        print(
            f"Message         : {result['text']}"
        )

        print(
            f"Thread          : "
            f"{result['conversation_id']}"
        )

        # ----------------------------------------------------
        # CONTEXT FOR TOP RESULT
        # ----------------------------------------------------

        if rank == 1:

            context = get_context(
                messages,
                result,
                context_size=5
            )

            print("\n" + "-" * 80)
            print("SURROUNDING CONVERSATION")
            print("-" * 80)

            for message in context:

                if message["id"] == result["id"]:

                    print(
                        f"\n⭐ "
                        f"[{message['timestamp']}] "
                        f"{message['sender']}: "
                        f"{message['text']}"
                    )

                else:

                    print(
                        f"\n   "
                        f"[{message['timestamp']}] "
                        f"{message['sender']}: "
                        f"{message['text']}"
                    )

        print("\n" + "-" * 80)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("SMART GROUP CHAT — HYBRID SEARCH")
    print("=" * 80)

    # --------------------------------------------------------
    # LOAD MESSAGES
    # --------------------------------------------------------

    print("\nLoading messages...")

    messages = load_messages()

    print(
        f"Loaded {len(messages)} messages."
    )

    # --------------------------------------------------------
    # BM25
    # --------------------------------------------------------

    print("\nBuilding BM25 index...")

    bm25 = build_bm25(messages)

    print("BM25 ready.")

    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    print("\nLoading semantic model...")

    model = SentenceTransformer(
        MODEL_NAME
    )

    print("Semantic model ready.")

    # --------------------------------------------------------
    # FAISS
    # --------------------------------------------------------

    print("\nLoading FAISS index...")

    if not FAISS_INDEX_FILE.exists():

        print(
            "\nERROR: FAISS index not found."
        )

        print(
            "Run semantic_search.py first."
        )

        return

    faiss_index = faiss.read_index(
        str(FAISS_INDEX_FILE)
    )

    print(
        f"FAISS loaded: "
        f"{faiss_index.ntotal} vectors"
    )

    # --------------------------------------------------------
    # READY
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print("HYBRID SEARCH READY")
    print("=" * 80)

    print("\nTry:")

    print(
        "  when did we decide on the trip"
    )

    print(
        "  what did Priya say about the budget"
    )

    print(
        "  what did we discuss last month"
    )

    print(
        "  Manali trip"
    )

    print("\nType 'exit' to quit.\n")

    # --------------------------------------------------------
    # SEARCH LOOP
    # --------------------------------------------------------

    while True:

        query = input(
            "Search: "
        ).strip()

        if query.lower() == "exit":

            print("\nGoodbye!")
            break

        if not query:
            continue

        # ----------------------------------------------------
        # QUERY ANALYSIS
        # ----------------------------------------------------

        query_info = analyze_query(
            query
        )

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        results = hybrid_search(
            query,
            messages,
            bm25,
            model,
            faiss_index,
            top_k=10
        )

        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        display_results(
            results,
            messages,
            query_info
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()