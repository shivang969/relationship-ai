import json
import os

try:
    import anthropic
    client = anthropic.Anthropic()
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    client = None

ACTION_TYPES = ["send_nudge", "follow_up_plan", "reconnect", "maintain", "check_in"]

SYSTEM_PROMPT = """You are a Relationship Intelligence AI. You analyze friendship/relationship data and make smart, empathetic decisions about how to help someone maintain their important relationships.
You receive structured data about a person's communication patterns and must:
1. Diagnose the relationship situation
2. Decide the best action
3. Draft a specific, natural message the user can send
Be concise, warm, and realistic. Messages should sound like a real person wrote them — not a bot.
Always respond in valid JSON format only."""

def build_context(scored_contact):
    return f"""
Contact: {scored_contact['contact']} ({scored_contact['relationship_type']})
Health Score: {scored_contact['health_score']}/100 (Grade: {scored_contact['grade']})
Key Metrics:
- Days since last contact: {scored_contact['days_since_last']}
- Messages last 30 days: {scored_contact['freq_recent_30d']} (prev 30d: {scored_contact['freq_prev_30d']})
- You initiate {round(scored_contact['my_start_ratio']*100)}% of conversations
- Avg reply latency: {scored_contact['avg_reply_latency_mins']} mins
- Sentiment score: {scored_contact['sentiment_score']} (-1 negative to +1 positive)
- Plan mentions: {scored_contact['plan_mentions']}
- Unresolved plans: {scored_contact.get('unresolved_plans', [])}
Detected Issues: {', '.join(scored_contact['anomalies']) if scored_contact['anomalies'] else 'None'}
Flags: {'; '.join(scored_contact['flags']) if scored_contact['flags'] else 'None'}
Last message: "{scored_contact['last_message_preview']}"
Last contact: {scored_contact['last_message_date']}
"""

def get_ai_decision(scored_contact):
    if not AI_AVAILABLE or client is None:
        return {
            "situation_summary": "AI unavailable — install anthropic package and set API key",
            "action_type": "check_in",
            "urgency": "medium",
            "reasoning": "Defaulting to check-in action",
            "draft_message": f"Hey {scored_contact['contact'].split()[0]}! Been a while — how are you doing?",
            "insight": "Regular check-ins help maintain relationship health."
        }

    context = build_context(scored_contact)
    prompt = f"""Analyze this relationship and provide your decision:
{context}
Respond with this exact JSON structure:
{{
  "situation_summary": "1-2 sentence diagnosis of what's happening",
  "action_type": "one of: {', '.join(ACTION_TYPES)}",
  "urgency": "low | medium | high",
  "reasoning": "Why this action makes sense given the data",
  "draft_message": "The actual message the user should send (natural, casual, 1-3 sentences)",
  "insight": "One data-driven insight about this relationship pattern"
}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        return {
            "situation_summary": "Unable to analyze — API error",
            "action_type": "check_in",
            "urgency": "medium",
            "reasoning": str(e),
            "draft_message": f"Hey {scored_contact['contact'].split()[0]}! Been a while — how are you doing?",
            "insight": "Regular check-ins help maintain relationship health."
        }

def run_decision_engine(scored_contacts, top_n=6):
    priority_contacts = sorted(
        scored_contacts,
        key=lambda x: (0 if x["priority"] == "high" else 1 if x["priority"] == "medium" else 2, x["health_score"])
    )[:top_n]

    decisions = []
    for contact in priority_contacts:
        print(f"  → Analyzing {contact['contact']}...")
        decision = get_ai_decision(contact)
        decisions.append({**contact, "ai_decision": decision})

    return decisions