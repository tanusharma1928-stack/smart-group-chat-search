import json
import sqlite3
from pathlib import Path
from datetime import datetime

# PATHS

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

JSON_FILE = DATA_DIR / "chat.json"

DB_FILE = DATA_DIR / "chat.db"

# LOAD JSON DATA

def load_messages():

    if not JSON_FILE.exists():
        raise FileNotFoundError(
            f"Chat dataset not found: {JSON_FILE}"
        )

    with open(JSON_FILE, "r", encoding="utf-8") as file:
        messages = json.load(file)

    return messages


# VALIDATE DATASET

def validate_messages(messages):

    print("\n" + "=" * 60)
    print("DATASET VALIDATION")
    print("=" * 60)

    # Total messages

    print(f"Total messages: {len(messages)}")

    if len(messages) >= 4000:
        print("✓ Message count requirement satisfied")
    else:
        print("✗ Message count is below 4000")

    # Participants

    participants = set(
        message["sender"]
        for message in messages
    )

    print(f"\nParticipants: {len(participants)}")

    for person in sorted(participants):
        print(f"  ✓ {person}")

    if len(participants) >= 8:
        print("✓ Participant requirement satisfied")
    else:
        print("✗ Need at least 8 participants")

    # Dates

    timestamps = [
        datetime.fromisoformat(message["timestamp"])
        for message in messages
    ]

    earliest = min(timestamps)
    latest = max(timestamps)

    print(f"\nEarliest message: {earliest}")
    print(f"Latest message:   {latest}")

    duration_days = (latest - earliest).days

    print(f"Chat duration:    {duration_days} days")

    if duration_days >= 150:
        print("✓ Six-month duration requirement approximately satisfied")
    else:
        print("✗ Chat duration is too short")

    # Forwarded messages

    forwarded = sum(
        1
        for message in messages
        if message["is_forwarded"]
    )

    print(f"\nForwarded messages: {forwarded}")

    if forwarded > 0:
        print("✓ Forwarded messages found")
    else:
        print("✗ No forwarded messages found")

    # Conversation threads

    conversations = set(
        message["conversation_id"]
        for message in messages
        if message["conversation_id"] is not None
    )

    print("\nSpecial decision threads:")

    for conversation in sorted(conversations):
        count = sum(
            1
            for message in messages
            if message["conversation_id"] == conversation
        )

        print(f"  ✓ {conversation}: {count} messages")

    # Required fields

    required_fields = [
        "id",
        "timestamp",
        "sender",
        "text",
        "is_forwarded",
        "conversation_id"
    ]

    invalid_messages = []

    for message in messages:

        missing = [
            field
            for field in required_fields
            if field not in message
        ]

        if missing:
            invalid_messages.append(
                (message.get("id"), missing)
            )

    if len(invalid_messages) == 0:
        print("\n✓ All messages contain required fields")
    else:
        print(
            f"\n✗ {len(invalid_messages)} messages have missing fields"
        )

    print("=" * 60)


# CREATE DATABASE

def create_database(messages):

    print("\nCreating SQLite database...")

    connection = sqlite3.connect(DB_FILE)

    cursor = connection.cursor()

    # Create table

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY,

            timestamp TEXT NOT NULL,

            sender TEXT NOT NULL,

            text TEXT NOT NULL,

            is_forwarded INTEGER NOT NULL,

            conversation_id TEXT

        )
    """)

    # Clear old data

    cursor.execute("DELETE FROM messages")

    # Insert messages

    for message in messages:

        cursor.execute("""
            INSERT INTO messages
            (
                id,
                timestamp,
                sender,
                text,
                is_forwarded,
                conversation_id
            )

            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            message["id"],
            message["timestamp"],
            message["sender"],
            message["text"],
            int(message["is_forwarded"]),
            message["conversation_id"]
        ))

    connection.commit()

    # Verify database

    cursor.execute(
        "SELECT COUNT(*) FROM messages"
    )

    count = cursor.fetchone()[0]

    print(f"Messages inserted into database: {count}")

    # Create indexes

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sender
        ON messages(sender)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp
        ON messages(timestamp)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversation
        ON messages(conversation_id)
    """)

    connection.commit()

    connection.close()

    print(f"✓ Database created: {DB_FILE}")

# MAIN

def main():

    messages = load_messages()

    validate_messages(messages)

    create_database(messages)

    print("\n" + "=" * 60)
    print("PHASE 2 COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()