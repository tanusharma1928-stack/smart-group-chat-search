import sqlite3
from pathlib import Path

# PATH

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "data" / "chat.db"

# LOAD MESSAGE

def get_message(message_id):

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
        WHERE id = ?
    """, (message_id,))

    message = cursor.fetchone()

    connection.close()

    if message is None:
        return None

    return dict(message)

# GET SURROUNDING MESSAGES

def get_context(message_id, context_size=5):

    connection = sqlite3.connect(DB_FILE)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # First get the target message

    cursor.execute("""
        SELECT
            id,
            timestamp,
            sender,
            text,
            is_forwarded,
            conversation_id
        FROM messages
        WHERE id = ?
    """, (message_id,))

    target = cursor.fetchone()

    if target is None:

        connection.close()

        return []

    target = dict(target)

    # Get messages before and after the target

    cursor.execute("""
        SELECT
            id,
            timestamp,
            sender,
            text,
            is_forwarded,
            conversation_id
        FROM messages
        WHERE id BETWEEN ? AND ?
        ORDER BY id
    """, (
        message_id - context_size,
        message_id + context_size
    ))

    messages = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return messages


# DISPLAY CONTEXT

def display_context(messages, target_id):

    print("\n")
    print("=" * 80)
    print("CONVERSATION CONTEXT")
    print("=" * 80)

    if not messages:

        print("No context found.")

        return

    for message in messages:

        message_id = message["id"]

        timestamp = message["timestamp"]

        sender = message["sender"]

        text = message["text"]
    
        # Highlight the matched message

        if message_id == target_id:

            print(
                f"\n⭐ [{timestamp}] {sender}: {text}"
            )

        else:

            print(
                f"\n   [{timestamp}] {sender}: {text}"
            )

    print("\n" + "=" * 80)


# MAIN

def main():

    print("=" * 80)
    print("SMART GROUP CHAT — CONTEXT RETRIEVER")
    print("=" * 80)

    print("\nEnter a message ID.")

    print("Example: 1904")

    print("Type 'exit' to quit.\n")

    while True:

        user_input = input(
            "Message ID: "
        ).strip()

        if user_input.lower() == "exit":

            print("\nGoodbye!")

            break

        if not user_input.isdigit():

            print(
                "Please enter a valid numeric message ID."
            )

            continue

        message_id = int(user_input)

        context = get_context(
            message_id,
            context_size=5
        )

        display_context(
            context,
            message_id
        )

# RUN

if __name__ == "__main__":

    main()