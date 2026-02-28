import json
import random
import os
from datetime import datetime, timedelta

random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONTACTS = [
    {"name": "Aarav Shah",       "type": "close_friend",    "pattern": "healthy"},
    {"name": "Priya Nair",       "type": "college_friend",  "pattern": "drifting"},
    {"name": "Rohan Mehta",      "type": "project_partner", "pattern": "one_sided"},
    {"name": "Sneha Kulkarni",   "type": "close_friend",    "pattern": "healthy"},
    {"name": "Dev Patel",        "type": "acquaintance",    "pattern": "dormant"},
    {"name": "Meera Iyer",       "type": "college_friend",  "pattern": "drifting"},
    {"name": "Kabir Sharma",     "type": "project_partner", "pattern": "healthy"},
    {"name": "Ananya Gupta",     "type": "close_friend",    "pattern": "one_sided"},
    {"name": "Vikas Rao",        "type": "acquaintance",    "pattern": "dormant"},
    {"name": "Tanya Bose",       "type": "college_friend",  "pattern": "drifting"},
]

ME = "You"

HEALTHY_MSGS = [
    ("Hey! How's the internship going?", True),
    ("It's great! Super busy but loving it. You?", False),
    ("Same tbh. Let's catch up this weekend?", True),
    ("Yes! Saturday works for me 🙌", False),
    ("Btw did you see the new project brief?", True),
    ("Yeah, looks intense. We should plan together", False),
    ("Agreed. Coffee at 4pm Saturday?", True),
    ("Perfect. See you then!", False),
    ("Also happy birthday btw!! 🎂", True),
    ("Omg thank you!! That means a lot", False),
]

DRIFTING_MSGS = [
    ("Hey it's been a while!", True),
    ("Yeah I know sorry been swamped", False),
    ("No worries. Miss hanging out", True),
    ("Same.. we should plan something", False),
    ("Definitely. Let me know when you're free", True),
    ("Will do!", False),
]

ONE_SIDED_MSGS = [
    ("Hey are you free this weekend?", True),
    ("Hey did you get my message?", True),
    ("Just checking in, hope you're okay", True),
    ("Yo long time no talk!", True),
    ("Hey! Hope everything's good", True),
    ("Miss ya, let's catch up soon", True),
    ("Hey you there?", True),
    ("Finally replied sorry was super busy", False),
    ("No worries! How have you been?", True),
    ("Good good. Busy with stuff", False),
]

DORMANT_MSGS = [
    ("Hey! Good seeing you at the event", True),
    ("Yeah same! We should hang sometime", False),
    ("Definitely, will ping you", True),
]

PLAN_MSGS = [
    "Let's meet next Friday for sure",
    "We should plan a trip in December",
    "I'll call you this weekend",
    "Let's study together tomorrow at 5",
]

SENTIMENT_POSITIVE = ["That's amazing!", "So happy for you!", "Love that!", "Proud of you!", "This is great news"]
SENTIMENT_NEGATIVE = ["I'm really stressed about this", "Feeling overwhelmed honestly", "Not doing great", "This sucks", "Super anxious lately"]

def gen_messages(pattern, contact_name, days_back=90):
    msgs = []
    now = datetime.now()

    if pattern == "healthy":
        template = HEALTHY_MSGS
        freq_days = 3
        start = now - timedelta(days=days_back)
        t = start
        cycle = 0
        while t < now:
            for text, is_me in template:
                sender = ME if is_me else contact_name
                msgs.append({"timestamp": t.isoformat(), "sender": sender, "receiver": contact_name if is_me else ME, "message": text, "contact": contact_name})
                t += timedelta(hours=random.randint(1, 8))
            if cycle % 3 == 0:
                msgs.append({"timestamp": t.isoformat(), "sender": ME, "receiver": contact_name, "message": random.choice(PLAN_MSGS), "contact": contact_name})
            t += timedelta(days=freq_days + random.randint(0, 3))
            cycle += 1

    elif pattern == "drifting":
        template = DRIFTING_MSGS
        start = now - timedelta(days=days_back)
        t = start
        for text, is_me in template:
            sender = ME if is_me else contact_name
            msgs.append({"timestamp": t.isoformat(), "sender": sender, "receiver": contact_name if is_me else ME, "message": text, "contact": contact_name})
            t += timedelta(hours=random.randint(2, 12))
        t = now - timedelta(days=25)
        msgs.append({"timestamp": t.isoformat(), "sender": contact_name, "receiver": ME, "message": "Hey we really should catch up soon!", "contact": contact_name})

    elif pattern == "one_sided":
        template = ONE_SIDED_MSGS
        t = now - timedelta(days=60)
        for text, is_me in template:
            sender = ME if is_me else contact_name
            msgs.append({"timestamp": t.isoformat(), "sender": sender, "receiver": contact_name if is_me else ME, "message": text, "contact": contact_name})
            t += timedelta(days=random.randint(3, 7) if is_me else 1, hours=random.randint(1, 5))

    elif pattern == "dormant":
        template = DORMANT_MSGS
        t = now - timedelta(days=75)
        for text, is_me in template:
            sender = ME if is_me else contact_name
            msgs.append({"timestamp": t.isoformat(), "sender": sender, "receiver": contact_name if is_me else ME, "message": text, "contact": contact_name})
            t += timedelta(hours=random.randint(4, 24))

    if random.random() > 0.4 and msgs:
        t_sent = datetime.fromisoformat(msgs[-1]["timestamp"]) + timedelta(hours=2)
        pool = SENTIMENT_POSITIVE if pattern == "healthy" else SENTIMENT_NEGATIVE
        msgs.append({"timestamp": t_sent.isoformat(), "sender": ME, "receiver": contact_name, "message": random.choice(pool), "contact": contact_name})

    return msgs

def generate_dataset():
    all_messages = []
    for c in CONTACTS:
        msgs = gen_messages(c["pattern"], c["name"])
        all_messages.extend(msgs)
    all_messages.sort(key=lambda x: x["timestamp"])

    out_path = os.path.join(BASE_DIR, "chats.json")
    with open(out_path, "w") as f:
        json.dump({"messages": all_messages, "contacts": CONTACTS}, f, indent=2)
    print(f"Generated {len(all_messages)} messages across {len(CONTACTS)} contacts.")
    print(f"Saved to: {out_path}")

if __name__ == "__main__":
    generate_dataset()