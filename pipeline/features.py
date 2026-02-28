import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

ME = "You"

PLAN_KEYWORDS = ["let's meet", "let's catch", "we should", "plan", "this weekend", "tomorrow",
                 "next week", "i'll call", "call you", "lunch", "coffee", "study together", "trip", "hangout", "hang out"]

def load_data(path=None):
    import json
    if path is None:
        path = os.path.join(DATA_DIR, "chats.json")
    with open(path) as f:
        data = json.load(f)
    df = pd.DataFrame(data["messages"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    contacts_meta = {c["name"]: c for c in data["contacts"]}
    return df, contacts_meta

def extract_features(df, contact_name, reference_date=None):
    if reference_date is None:
        reference_date = datetime.now()

    cdf = df[df["contact"] == contact_name].copy().sort_values("timestamp")
    if cdf.empty:
        return {}

    now = pd.Timestamp(reference_date)
    total_msgs = len(cdf)
    my_msgs = cdf[cdf["sender"] == ME]
    their_msgs = cdf[cdf["sender"] == contact_name]

    last_msg_time = cdf["timestamp"].max()
    days_since_last = (now - last_msg_time).days

    last_30 = cdf[cdf["timestamp"] >= now - timedelta(days=30)]
    prev_30 = cdf[(cdf["timestamp"] >= now - timedelta(days=60)) & (cdf["timestamp"] < now - timedelta(days=30))]
    freq_recent = len(last_30)
    freq_prev = len(prev_30)
    freq_trend = freq_recent - freq_prev

    initiation_ratio = len(my_msgs) / max(total_msgs, 1)

    cdf = cdf.copy()
    cdf["gap"] = cdf["timestamp"].diff().dt.total_seconds().fillna(99999)
    starters = cdf[cdf["gap"] > 6 * 3600]
    my_starts = len(starters[starters["sender"] == ME])
    their_starts = len(starters[starters["sender"] == contact_name])
    total_starts = my_starts + their_starts
    start_ratio = my_starts / max(total_starts, 1)

    reply_times = []
    msgs_list = cdf.reset_index(drop=True)
    for i in range(1, len(msgs_list)):
        prev = msgs_list.iloc[i - 1]
        curr = msgs_list.iloc[i]
        if prev["sender"] != curr["sender"]:
            gap_mins = (curr["timestamp"] - prev["timestamp"]).total_seconds() / 60
            if gap_mins < 1440:
                reply_times.append(gap_mins)
    avg_reply_latency = np.mean(reply_times) if reply_times else 999

    positive_words = ["great", "amazing", "love", "happy", "excited", "proud", "good", "thanks", "thank", "awesome", "perfect"]
    negative_words = ["stressed", "overwhelmed", "anxious", "sucks", "bad", "tired", "busy", "sorry", "miss", "worried"]
    all_text = " ".join(cdf["message"].tolist()).lower()
    pos_count = sum(all_text.count(w) for w in positive_words)
    neg_count = sum(all_text.count(w) for w in negative_words)
    sentiment_score = (pos_count - neg_count) / max(pos_count + neg_count, 1)

    plan_msgs = cdf[cdf["message"].str.lower().apply(lambda x: any(kw in x for kw in PLAN_KEYWORDS))]
    plan_count = len(plan_msgs)
    unresolved_plans = []
    for _, row in plan_msgs.iterrows():
        days_after_plan = (now - row["timestamp"]).days
        if days_after_plan > 7:
            msgs_after = cdf[cdf["timestamp"] > row["timestamp"]]
            if len(msgs_after) < 2:
                unresolved_plans.append(row["message"])

    if len(cdf) > 1:
        gaps = cdf["timestamp"].diff().dt.days.dropna()
        avg_gap = gaps.mean()
        silence_ratio = days_since_last / max(avg_gap, 1)
    else:
        avg_gap = 0
        silence_ratio = 1

    return {
        "contact": contact_name,
        "total_messages": total_msgs,
        "days_since_last": days_since_last,
        "freq_recent_30d": freq_recent,
        "freq_prev_30d": freq_prev,
        "freq_trend": freq_trend,
        "my_message_ratio": round(initiation_ratio, 3),
        "my_start_ratio": round(start_ratio, 3),
        "avg_reply_latency_mins": round(avg_reply_latency, 1),
        "sentiment_score": round(sentiment_score, 3),
        "plan_mentions": plan_count,
        "unresolved_plans": unresolved_plans,
        "avg_gap_days": round(avg_gap, 1),
        "silence_ratio": round(silence_ratio, 2),
        "last_message_date": last_msg_time.strftime("%Y-%m-%d"),
        "last_message_preview": cdf.iloc[-1]["message"][:80],
    }

def extract_all_features(df, contacts_meta):
    all_features = []
    for name in contacts_meta:
        f = extract_features(df, name)
        if f:
            f["relationship_type"] = contacts_meta[name]["type"]
            f["true_pattern"] = contacts_meta[name]["pattern"]
            all_features.append(f)
    return all_features