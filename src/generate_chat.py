import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# CONFIGURATION

TOTAL_MESSAGES = 5000

PARTICIPANTS = [
    "Aman",
    "Priya",
    "Rahul",
    "Neha",
    "Karan",
    "Sneha",
    "Arjun",
    "Riya"
]

START_DATE = datetime(2026, 1, 1, 8, 0, 0)
END_DATE = datetime(2026, 6, 30, 23, 59, 59)

random.seed(42)

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = DATA_DIR / "chat.json"


# MESSAGE TEMPLATES

CASUAL_MESSAGES = [
    "kya scene hai?",
    "bhai kya kar rahe ho?",
    "kal mil rahe?",
    "haan bhai",
    "okay",
    "okk",
    "done",
    "sure",
    "wait 2 min",
    "ruk bhai",
    "abhi busy hu",
    "later dekhte hain",
    "haan sahi hai",
    "nice 😂",
    "lol",
    "arre yaar",
    "kuch nahi",
    "same bro",
    "mood nahi hai aaj",
    "chal dekhte hain",
    "haan possible hai",
    "not sure",
    "maybe",
    "exactly 😂",
    "true",
    "agreed",
    "bruh",
    "😂😂",
    "😭",
    "👍",
    "haan haan",
]

HINGLISH_MESSAGES = [
    "bhai kal college jana hai kya?",
    "assignment submit kiya?",
    "yaar ye topic samajh nahi aa raha",
    "kal ka plan kya hai?",
    "khana kha liya?",
    "aaj lecture attend karoge?",
    "bhai notes bhej dena",
    "exam ka kya scene hai?",
    "ye wala idea better lag raha hai",
    "budget thoda zyada ho jayega",
    "5 min mein call karta hu",
    "bhai mujhe bhi add kar lena",
    "kal milke discuss karte hain",
    "ye kaam aaj hi finish karna hai",
    "arre ye toh mast hai",
    "mujhe lagta hai ye sahi rahega",
    "dekhte hain kya hota hai",
    "haan ye possible hai",
    "abhi confirm nahi hai",
    "bhai jaldi bata",
    "koi update hai?",
    "main check karta hu",
    "wait kar thoda",
    "haan bhai fix hai",
    "kal pakka?",
    "scene sorted hai",
]

TYPO_MESSAGES = [
    "kal milte h",
    "kya kr rhe ho",
    "haan dekhte h",
    "mujhe nhi pta",
    "mai aa jaunga",
    "budget kitna h?",
    "ye sahi h",
    "done bhaii",
    "thoda late ho jyega",
    "ruk 2 min",
    "abhi ata hu",
    "kaha ho?",
    "kab jana h?",
    "final krde?",
    "haan kr sakte",
    "mujhe bhi btana",
    "notes bhej do pls",
    "assignment hua kya",
    "kal ka kya scene h",
    "haan bhai sure",
]

TECH_MESSAGES = [
    "code run nahi ho raha",
    "server down hai kya?",
    "git push kar diya",
    "deployment check karo",
    "API ka response slow aa raha hai",
    "database connection issue hai",
    "logs dekhe kya?",
    "frontend ready hai",
    "backend mein thoda kaam baki hai",
    "branch merge kar du?",
    "PR raise kar diya",
    "bug fix ho gaya",
    "production pe test karna",
    "localhost pe toh chal raha hai",
    "error samajh nahi aa raha",
]

COLLEGE_MESSAGES = [
    "professor ne assignment extend kiya kya?",
    "internal ke marks aa gaye?",
    "lab mein attendance lagegi?",
    "presentation kab hai?",
    "sir ne kal viva bola hai",
    "notes mil sakte hain?",
    "exam timetable check kiya?",
    "project submission kab hai?",
    "attendance ka kya scene hai?",
    "aaj class cancel hai kya?",
]

FOOD_MESSAGES = [
    "kuch order karein?",
    "pizza?",
    "chai peene chale?",
    "aaj mess mein kya hai?",
    "momos?",
    "bhai bhook lagi hai",
    "Swiggy karu?",
    "kya kha rahe ho?",
    "coffee?",
    "dinner ka plan?",
]

MEME_MESSAGES = [
    "ye meme dekho 😂",
    "bhai ye literally hum hain 😭",
    "😂😂😂",
    "no way bro",
    "this is too accurate",
    "I can't 😂",
    "same energy",
    "bro got cooked 💀",
]

FORWARDED_MESSAGES = [
    "Forwarded:\nTomorrow college will remain closed due to maintenance.",
    "Forwarded:\nImportant notice: Assignment submission deadline extended.",
    "Forwarded:\nFlash sale starts at 8 PM today.",
    "Forwarded:\nWeather alert for the next 24 hours.",
    "Forwarded:\nPlease share this with everyone.",
    "Forwarded:\nEvent registration closes tonight.",
]


# RANDOM MESSAGE GENERATOR

def random_normal_message():
    category = random.choices(
        [
            CASUAL_MESSAGES,
            HINGLISH_MESSAGES,
            TYPO_MESSAGES,
            TECH_MESSAGES,
            COLLEGE_MESSAGES,
            FOOD_MESSAGES,
            MEME_MESSAGES,
            FORWARDED_MESSAGES
        ],
        weights=[22, 25, 15, 10, 10, 7, 6, 5],
        k=1
    )[0]

    return random.choice(category)


# TIMESTAMP GENERATOR

def generate_timestamp():
    total_seconds = int((END_DATE - START_DATE).total_seconds())

    random_seconds = random.randint(0, total_seconds)

    return START_DATE + timedelta(seconds=random_seconds)


# DECISION THREADS

def create_manali_thread():
    base = datetime(2026, 3, 12, 18, 30)

    messages = [
        ("Rahul", "guys trip ka kya scene hai?"),
        ("Priya", "iss baar kahin properly chalte hain"),
        ("Aman", "Manali chale?"),
        ("Neha", "haan but dates decide karo"),
        ("Karan", "14 se 17 kaisa rahega?"),
        ("Sneha", "mere liye works"),
        ("Arjun", "haan main free hu"),
        ("Riya", "same"),
        ("Priya", "travel kaise karenge?"),
        ("Rahul", "bus better rahegi I think"),
        ("Aman", "train se bhi dekh sakte"),
        ("Neha", "bus direct mil jayegi"),
        ("Karan", "hotel ka kya?"),
        ("Priya", "maine kuch options dekhe"),
        ("Priya", "ek 4.7k per person ke around hai"),
        ("Rahul", "location achi hai kya?"),
        ("Priya", "haan mall road ke near hai"),
        ("Sneha", "photos bhejo"),
        ("Priya", "ye wala dekho"),
        ("Arjun", "looks good"),
        ("Riya", "rooms kitne hain?"),
        ("Priya", "4 rooms available hain"),
        ("Neha", "perfect"),
        ("Aman", "budget 5k ke andar hai na?"),
        ("Priya", "haan approx 4.7k"),
        ("Rahul", "mere hisaab se ye best hai"),
        ("Karan", "book kar dein?"),
        ("Aman", "haan bhai ye wala final kar dete hain"),
        ("Neha", "done 👍"),
        ("Sneha", "finally 😂"),
        ("Arjun", "Manali locked then"),
        ("Riya", "lets gooo"),
    ]

    result = []

    for i, (sender, text) in enumerate(messages):
        result.append({
            "timestamp": (base + timedelta(minutes=i * random.randint(2, 8))).isoformat(),
            "sender": sender,
            "text": text,
            "is_forwarded": False,
            "conversation_id": "manali_trip"
        })

    return result


def create_college_event_thread():
    base = datetime(2026, 4, 20, 17, 0)

    messages = [
        ("Neha", "college event ka venue final karna hai"),
        ("Aman", "auditorium expensive hai"),
        ("Priya", "community hall check karo"),
        ("Rahul", "maine price pucha"),
        ("Rahul", "around 18k pad raha hai"),
        ("Karan", "auditorium kitna tha?"),
        ("Rahul", "almost 30k"),
        ("Sneha", "community hall better hai"),
        ("Arjun", "parking available hai?"),
        ("Priya", "haan available hai"),
        ("Riya", "food ka kya karenge?"),
        ("Neha", "outside catering allowed hai"),
        ("Aman", "budget ke andar aa jayega"),
        ("Karan", "date bhi lock karni hai"),
        ("Priya", "Saturday better rahega"),
        ("Rahul", "24th?")
        ,
        ("Neha", "works for me"),
        ("Sneha", "same"),
        ("Arjun", "haan"),
        ("Riya", "okay"),
        ("Aman", "then community hall on 24th?"),
        ("Priya", "yes final"),
        ("Neha", "done"),
        ("Karan", "I'll handle booking"),
    ]

    result = []

    for i, (sender, text) in enumerate(messages):
        result.append({
            "timestamp": (base + timedelta(minutes=i * random.randint(3, 9))).isoformat(),
            "sender": sender,
            "text": text,
            "is_forwarded": False,
            "conversation_id": "college_event"
        })

    return result


def create_purchase_thread():
    base = datetime(2026, 5, 10, 19, 15)

    messages = [
        ("Arjun", "project ke liye laptop lena hai"),
        ("Aman", "budget kitna hai?"),
        ("Priya", "around 60k max"),
        ("Rahul", "gaming laptop ki zarurat nahi hai"),
        ("Neha", "coding ke liye decent processor enough hai"),
        ("Karan", "16GB RAM hona chahiye"),
        ("Sneha", "SSD bhi at least 512"),
        ("Riya", "maine do options shortlist kiye"),
        ("Riya", "option A cheaper hai"),
        ("Riya", "option B mein better processor hai"),
        ("Arjun", "difference kitna hai?"),
        ("Riya", "around 5k"),
        ("Priya", "better processor worth it hai"),
        ("Rahul", "agree"),
        ("Neha", "battery bhi check karo"),
        ("Karan", "B ki battery better hai"),
        ("Aman", "then B makes more sense"),
        ("Sneha", "haan"),
        ("Arjun", "okay option B lete hain"),
        ("Riya", "final?"),
        ("Arjun", "yes final"),
        ("Priya", "done"),
    ]

    result = []

    for i, (sender, text) in enumerate(messages):
        result.append({
            "timestamp": (base + timedelta(minutes=i * random.randint(3, 10))).isoformat(),
            "sender": sender,
            "text": text,
            "is_forwarded": False,
            "conversation_id": "laptop_purchase"
        })

    return result


# GENERATE RANDOM CHAT

def generate_random_messages(count):
    messages = []

    for _ in range(count):
        timestamp = generate_timestamp()
        sender = random.choice(PARTICIPANTS)
        text = random_normal_message()

        is_forwarded = text.startswith("Forwarded:")

        messages.append({
            "timestamp": timestamp.isoformat(),
            "sender": sender,
            "text": text,
            "is_forwarded": is_forwarded,
            "conversation_id": None
        })

    return messages


# MAIN

def main():

    # Generate the three important conversations first
    manali = create_manali_thread()
    event = create_college_event_thread()
    purchase = create_purchase_thread()

    special_messages = manali + event + purchase

    # Remaining messages
    random_count = TOTAL_MESSAGES - len(special_messages)

    random_messages = generate_random_messages(random_count)

    all_messages = random_messages + special_messages

    # Sort chronologically
    all_messages.sort(key=lambda x: x["timestamp"])

    # Add IDs
    for message_id, message in enumerate(all_messages, start=1):
        message["id"] = message_id

    # Save
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            all_messages,
            file,
            ensure_ascii=False,
            indent=2
        )

    # Statistics
    print("=" * 60)
    print("SYNTHETIC GROUP CHAT GENERATED")
    print("=" * 60)

    print(f"Total messages : {len(all_messages)}")
    print(f"Participants   : {len(PARTICIPANTS)}")
    print(f"Start date     : {START_DATE.date()}")
    print(f"End date       : {END_DATE.date()}")
    print(f"Output file    : {OUTPUT_FILE}")

    print("\nParticipants:")

    for participant in PARTICIPANTS:
        count = sum(
            1 for message in all_messages
            if message["sender"] == participant
        )

        print(f"  {participant:<10} {count} messages")

    print("\nDecision threads:")
    print("  ✓ Manali Trip")
    print("  ✓ College Event")
    print("  ✓ Laptop Purchase")

    print("\nDataset generation complete!")


if __name__ == "__main__":
    main()