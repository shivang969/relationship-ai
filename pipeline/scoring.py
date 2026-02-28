import numpy as np

# ─── Scoring Weights ───────────────────────────────────────────────────────────
WEIGHTS = {
    "recency":      0.28,
    "frequency":    0.22,
    "reciprocity":  0.20,
    "sentiment":    0.15,
    "engagement":   0.15,
}

def score_recency(days_since_last):
    """0-100. Recent = high."""
    if days_since_last <= 2:   return 100
    if days_since_last <= 7:   return 85
    if days_since_last <= 14:  return 65
    if days_since_last <= 30:  return 40
    if days_since_last <= 60:  return 20
    return 5

def score_frequency(freq_recent, freq_trend):
    """0-100. Active + growing = high."""
    base = min(freq_recent * 4, 80)  # 20 msgs in 30d → 80pts
    trend_bonus = 10 if freq_trend > 0 else (-10 if freq_trend < -5 else 0)
    return max(0, min(100, base + trend_bonus))

def score_reciprocity(my_msg_ratio, my_start_ratio):
    """0-100. Balanced = high. One-sided = low."""
    # Perfect balance = 0.5, deviation penalized
    msg_balance = 1 - abs(my_msg_ratio - 0.5) * 2     # 0-1
    start_balance = 1 - abs(my_start_ratio - 0.5) * 2  # 0-1
    combined = (msg_balance * 0.5 + start_balance * 0.5)
    return round(combined * 100)

def score_sentiment(sentiment_score):
    """0-100. Positive = high."""
    # sentiment_score is -1 to 1
    return round((sentiment_score + 1) / 2 * 100)

def score_engagement(total_msgs, plan_mentions, avg_reply_latency):
    """0-100. Deep engagement = high."""
    depth = min(total_msgs / 2, 40)  # up to 40pts from volume
    plan_bonus = min(plan_mentions * 5, 20)  # up to 20pts from plans
    # Latency: < 30 min = 40pts, up to 1440 min = 0pts
    latency_score = max(0, 40 - (avg_reply_latency / 36))
    return round(min(100, depth + plan_bonus + latency_score))

def compute_health_score(features):
    r = score_recency(features["days_since_last"])
    f = score_frequency(features["freq_recent_30d"], features["freq_trend"])
    rec = score_reciprocity(features["my_message_ratio"], features["my_start_ratio"])
    s = score_sentiment(features["sentiment_score"])
    e = score_engagement(features["total_messages"], features["plan_mentions"], features["avg_reply_latency_mins"])

    weighted = (
        r   * WEIGHTS["recency"] +
        f   * WEIGHTS["frequency"] +
        rec * WEIGHTS["reciprocity"] +
        s   * WEIGHTS["sentiment"] +
        e   * WEIGHTS["engagement"]
    )

    score = round(weighted)

    if score >= 75:   grade = "A"
    elif score >= 55: grade = "B"
    elif score >= 35: grade = "C"
    else:             grade = "D"

    subscores = {"recency": r, "frequency": f, "reciprocity": rec, "sentiment": s, "engagement": e}

    return {"health_score": score, "grade": grade, "subscores": subscores}


# ─── Anomaly Detection ─────────────────────────────────────────────────────────
def detect_anomalies(features):
    anomalies = []
    flags = []

    d = features["days_since_last"]
    avg_gap = features["avg_gap_days"] or 1
    silence_ratio = features["silence_ratio"]

    # 1. Sudden silence
    if silence_ratio > 3 and d > 14:
        anomalies.append("sudden_silence")
        flags.append(f"Silent for {d} days — {round(silence_ratio)}x longer than usual")

    # 2. One-sided conversation
    if features["my_start_ratio"] > 0.75 and features["total_messages"] > 5:
        anomalies.append("one_sided")
        flags.append(f"You initiate {round(features['my_start_ratio']*100)}% of conversations")

    # 3. Frequency decay
    if features["freq_trend"] < -8:
        anomalies.append("frequency_decay")
        flags.append(f"Activity dropped from {features['freq_prev_30d']} → {features['freq_recent_30d']} msgs/month")

    # 4. Unresolved plans
    if features["unresolved_plans"]:
        anomalies.append("unresolved_plans")
        flags.append(f"{len(features['unresolved_plans'])} plan(s) mentioned but never followed up")

    # 5. Dormant relationship
    if d > 45:
        anomalies.append("dormant")
        flags.append(f"No contact in {d} days — relationship may be fading")

    # 6. Negative sentiment drift
    if features["sentiment_score"] < -0.3:
        anomalies.append("negative_sentiment")
        flags.append("Recent conversations have a negative emotional tone")

    priority = "high" if len(anomalies) >= 2 else ("medium" if len(anomalies) == 1 else "low")

    return {"anomalies": anomalies, "flags": flags, "priority": priority}


def score_all(features_list):
    results = []
    for f in features_list:
        score_data = compute_health_score(f)
        anomaly_data = detect_anomalies(f)
        results.append({**f, **score_data, **anomaly_data})
    results.sort(key=lambda x: x["health_score"])
    return results
