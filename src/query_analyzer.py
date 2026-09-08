import re
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta


BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "data" / "chat.db"


def get_participants():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT sender FROM messages")
    participants = [row[0] for row in cursor.fetchall()]

    conn.close()
    return participants


def get_date_range(text):
    text = text.lower().strip()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM messages")
    min_date, max_date = cursor.fetchone()

    conn.close()

    if not max_date:
        return None, None

    max_dt = datetime.fromisoformat(max_date)

    # -------------------------
    # LAST MONTH
    # -------------------------
    if "last month" in text or "previous month" in text:
        first_this_month = max_dt.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        last_day_previous_month = first_this_month - timedelta(days=1)

        start = last_day_previous_month.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        return start.isoformat(), first_this_month.isoformat()

    # -------------------------
    # THIS MONTH
    # -------------------------
    if "this month" in text:
        start = max_dt.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        return start.isoformat(), max_dt.isoformat()

    # -------------------------
    # LAST WEEK
    # -------------------------
    if "last week" in text or "previous week" in text:
        end = max_dt
        start = end - timedelta(days=7)

        return start.isoformat(), end.isoformat()

    # -------------------------
    # THIS WEEK
    # -------------------------
    if "this week" in text:
        start = max_dt - timedelta(days=max_dt.weekday())

        start = start.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        return start.isoformat(), max_dt.isoformat()

    return None, None


def find_person(query, participants):
    query_lower = query.lower()

    # Check longest names first
    participants = sorted(
        participants,
        key=lambda x: len(x),
        reverse=True
    )

    for person in participants:
        pattern = r"\b" + re.escape(person.lower()) + r"\b"

        if re.search(pattern, query_lower):
            return person

    return None


def analyze_query(query):
    participants = get_participants()

    detected_person = find_person(
        query,
        participants
    )

    start_date, end_date = get_date_range(query)

    # -------------------------
    # QUERY TYPE
    # -------------------------

    if detected_person:
        query_type = "attributed"

    elif start_date is not None:
        query_type = "temporal"

    else:
        query_type = "semantic"

    return {
        "query": query,
        "type": query_type,
        "person": detected_person,
        "start_date": start_date,
        "end_date": end_date
    }


def main():

    print("=" * 70)
    print("QUERY ANALYZER")
    print("=" * 70)

    print("\nExamples:")
    print("1. when did we decide on the trip")
    print("2. what did Priya say about the budget")
    print("3. what did we discuss last month")
    print("4. what did we discuss last week")
    print("5. what did Priya say this month")

    print("\nType 'exit' to quit.\n")

    while True:

        query = input("Query: ").strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        result = analyze_query(query)

        print("\nQUERY ANALYSIS")
        print("-" * 50)

        print("Type       :", result["type"])
        print("Person     :", result["person"])
        print("Start Date :", result["start_date"])
        print("End Date   :", result["end_date"])

        print("-" * 50)


if __name__ == "__main__":
    main()