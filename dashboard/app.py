import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

OUTPUT_PATH = os.path.join(ROOT_DIR, "data", "pipeline_output.json")
CHATS_PATH  = os.path.join(ROOT_DIR, "data", "chats.json")

import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="RelAI — Relationship Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.stApp { background: #0a0a0f; color: #e8e8f0; }
.main-title { font-size: 2.8rem; font-weight: 700; background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1px; }
.subtitle { color: #6b7280; font-size: 0.95rem; margin-top: 4px; }
.action-card { background: linear-gradient(135deg, #1a0f2e, #0f1a2e); border: 1px solid #3730a3; border-radius: 16px; padding: 20px 24px; margin-bottom: 12px; }
.draft-message { background: #0f172a; border-left: 3px solid #a78bfa; padding: 12px 16px; border-radius: 0 10px 10px 0; font-style: italic; color: #cbd5e1; font-size: 0.9rem; margin-top: 10px; }
.insight-box { background: #0c1a0c; border: 1px solid #166534; border-radius: 10px; padding: 10px 14px; color: #86efac; font-size: 0.82rem; margin-top: 10px; }
.section-header { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; color: #4b5563; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #1f1f2e; }
.grade-badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.grade-A { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.grade-B { background: #1e3a5f; color: #60a5fa; border: 1px solid #1d4ed8; }
.grade-C { background: #3f2700; color: #fbbf24; border: 1px solid #92400e; }
.grade-D { background: #3f0f0f; color: #f87171; border: 1px solid #991b1b; }
.flag-pill { display: inline-block; background: #1f1f2e; border: 1px solid #2a2a3e; color: #94a3b8; padding: 4px 10px; border-radius: 20px; font-size: 0.72rem; margin: 3px; }
div[data-testid="stSidebar"] { background: #0d0d14 !important; border-right: 1px solid #1f1f2e; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_pipeline_output():
    if not os.path.exists(OUTPUT_PATH):
        return None
    with open(OUTPUT_PATH) as f:
        return json.load(f)

@st.cache_data
def load_chats():
    if not os.path.exists(CHATS_PATH):
        return pd.DataFrame()
    with open(CHATS_PATH) as f:
        data = json.load(f)
    df = pd.DataFrame(data["messages"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

def run_pipeline_now(use_ai=True):
    st.cache_data.clear()
    from main import run_pipeline
    with st.spinner("Running pipeline..."):
        run_pipeline(use_ai=use_ai)
    st.rerun()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 RelAI")
    st.markdown("<span style='color:#6b7280; font-size:0.8rem'>Relationship Intelligence</span>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<div class='section-header'>PIPELINE</div>", unsafe_allow_html=True)
    if st.button("▶  Run Pipeline (with AI)", use_container_width=True, type="primary"):
        run_pipeline_now(use_ai=True)
    if st.button("⚡ Run Pipeline (no AI)", use_container_width=True):
        run_pipeline_now(use_ai=False)
    if st.button("🔄 Generate New Data", use_container_width=True):
        from data.synthetic_generator import generate_dataset
        generate_dataset()
        if os.path.exists(OUTPUT_PATH):
            os.remove(OUTPUT_PATH)
        st.cache_data.clear()
        st.success("New data generated!")
        st.rerun()
    st.divider()
    st.markdown("<div class='section-header'>NAVIGATION</div>", unsafe_allow_html=True)
    page = st.radio("", ["📊 Dashboard", "👥 All Contacts", "🤖 AI Actions", "💬 Conversation View"], label_visibility="collapsed")

# ── Load ───────────────────────────────────────────────────────────────────────
data = load_pipeline_output()
chats_df = load_chats()

if data is None:
    st.markdown("<div class='main-title'>RelAI</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>AI-powered relationship intelligence pipeline</div>", unsafe_allow_html=True)
    st.info("No pipeline data yet. Click **▶ Run Pipeline** in the sidebar to start.")
    st.stop()

scored    = data["scored_contacts"]
decisions = data["ai_decisions"]
summary   = data["summary"]
run_time  = data.get("pipeline_run", "")

grade_colors  = {"A": "#4ade80", "B": "#60a5fa", "C": "#fbbf24", "D": "#f87171"}
pattern_icons = {"healthy": "💚", "drifting": "🟡", "one_sided": "🔴", "dormant": "⚫"}

# ══ DASHBOARD ══════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("<div class='main-title'>Relationship Intelligence</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>Last run: {run_time[:16].replace('T',' ')} · {len(scored)} contacts</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    avg_score = sum(c["health_score"] for c in scored) / len(scored)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Avg Health Score", f"{avg_score:.0f}/100")
    c2.metric("🟢 Healthy (A)", summary["grade_A"])
    c3.metric("🟡 At Risk (B/C)", summary["grade_B"] + summary["grade_C"])
    c4.metric("🔴 Critical (D)", summary["grade_D"])
    c5.metric("⚠️ High Priority", summary["high_priority"])

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1.2, 1])

    with col_l:
        st.markdown("<div class='section-header'>HEALTH SCORES</div>", unsafe_allow_html=True)
        srt = sorted(scored, key=lambda x: x["health_score"], reverse=True)
        fig = go.Figure(go.Bar(
            x=[c["health_score"] for c in srt],
            y=[c["contact"].split()[0] for c in srt],
            orientation="h",
            marker=dict(color=[grade_colors[c["grade"]] for c in srt], opacity=0.85),
            text=[f"{c['health_score']}/100" for c in srt],
            textposition="outside",
            textfont=dict(color="#9ca3af", size=11),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(range=[0,115], showgrid=True, gridcolor="#1f1f2e", tickfont=dict(color="#6b7280")),
            yaxis=dict(tickfont=dict(color="#e8e8f0", size=12)),
            margin=dict(l=10, r=50, t=10, b=10), height=320, showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown("<div class='section-header'>GRADE DISTRIBUTION</div>", unsafe_allow_html=True)
        fig2 = go.Figure(go.Pie(
            labels=["A — Healthy","B — Good","C — At Risk","D — Critical"],
            values=[summary["grade_A"], summary["grade_B"], summary["grade_C"], summary["grade_D"]],
            marker=dict(colors=["#4ade80","#60a5fa","#fbbf24","#f87171"], line=dict(color="#0a0a0f", width=3)),
            hole=0.6, textfont=dict(color="white", size=12), textposition="outside",
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=20,r=20,t=20,b=20), height=270,
            legend=dict(font=dict(color="#9ca3af", size=11), bgcolor="rgba(0,0,0,0)"),
            annotations=[dict(text=f"<b>{avg_score:.0f}</b>", x=0.5, y=0.5, font=dict(size=28, color="white"), showarrow=False)]
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>SUBSCORE RADAR — TOP 3</div>", unsafe_allow_html=True)
    top3 = sorted(scored, key=lambda x: x["health_score"], reverse=True)[:3]
    radar_cols = st.columns(3)
    categories = ["Recency","Frequency","Reciprocity","Sentiment","Engagement"]
    for i, c in enumerate(top3):
        ss = c["subscores"]
        vals = [ss["recency"], ss["frequency"], ss["reciprocity"], ss["sentiment"], ss["engagement"]]
        vals += [vals[0]]
        cats = categories + [categories[0]]
        fig3 = go.Figure(go.Scatterpolar(
            r=vals, theta=cats, fill="toself",
            fillcolor=f"rgba({int(grade_colors[c['grade']][1:3],16)},{int(grade_colors[c['grade']][3:5],16)},{int(grade_colors[c['grade']][5:7],16)},0.13)",
            line=dict(color=grade_colors[c["grade"]], width=2),
        ))
        fig3.update_layout(
            polar=dict(bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0,100], tickfont=dict(color="#6b7280", size=9), gridcolor="#1f1f2e"),
                angularaxis=dict(tickfont=dict(color="#9ca3af", size=10), gridcolor="#1f1f2e"),
            ),
            paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=30,r=30,t=40,b=30), height=220,
            title=dict(text=f"{c['contact'].split()[0]} — {c['health_score']}/100", font=dict(color="#e8e8f0", size=13), x=0.5)
        )
        radar_cols[i].plotly_chart(fig3, use_container_width=True)

# ══ ALL CONTACTS ═══════════════════════════════════════════════════════════════
elif page == "👥 All Contacts":
    st.markdown("<div class='main-title'>All Contacts</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Sorted by relationship health</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    f1, f2 = st.columns(2)
    grade_filter = f1.multiselect("Grade", ["A","B","C","D"], default=["A","B","C","D"])
    sort_by = f2.selectbox("Sort by", ["Health Score ↑", "Health Score ↓", "Days Silent ↓", "Name"])

    filtered = [c for c in scored if c["grade"] in grade_filter]
    if sort_by == "Health Score ↓":   filtered.sort(key=lambda x: x["health_score"], reverse=True)
    elif sort_by == "Health Score ↑": filtered.sort(key=lambda x: x["health_score"])
    elif sort_by == "Days Silent ↓":  filtered.sort(key=lambda x: x["days_since_last"], reverse=True)
    else:                              filtered.sort(key=lambda x: x["contact"])

    for c in filtered:
        icon = pattern_icons.get(c.get("true_pattern",""), "❓")
        with st.expander(f"{icon}  {c['contact']}  ·  {c['health_score']}/100  ·  Grade {c['grade']}  ·  {c['relationship_type'].replace('_',' ').title()}"):
            a, b, cc = st.columns(3)
            a.metric("Days Silent", c["days_since_last"])
            b.metric("Msgs (30d)", c["freq_recent_30d"])
            cc.metric("You Initiate", f"{round(c['my_start_ratio']*100)}%")
            d, e, ff = st.columns(3)
            d.metric("Avg Reply", f"{c['avg_reply_latency_mins']}m")
            e.metric("Sentiment", f"{c['sentiment_score']:+.2f}")
            ff.metric("Plan Mentions", c["plan_mentions"])
            if c["flags"]:
                for flag in c["flags"]:
                    st.markdown(f"<span class='flag-pill'>⚡ {flag}</span>", unsafe_allow_html=True)
            st.markdown(f"<br><span style='color:#6b7280;font-size:0.82rem'>Last: <em>\"{c['last_message_preview']}\"</em> — {c['last_message_date']}</span>", unsafe_allow_html=True)

# ══ AI ACTIONS ══════════════════════════════════════════════════════════════════
elif page == "🤖 AI Actions":
    st.markdown("<div class='main-title'>AI Action Center</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Automated decisions & drafted messages powered by Claude</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if not decisions:
        st.warning("No decisions yet. Run the pipeline first.")
        st.stop()

    action_icons = {"send_nudge":"📨","follow_up_plan":"📅","reconnect":"🔁","maintain":"✅","check_in":"👋"}
    urgency_map  = {"high":"🔴 HIGH","medium":"🟡 MEDIUM","low":"🟢 LOW"}

    for d in decisions:
        ai = d.get("ai_decision")
        if not ai:
            anomalies = d.get("anomalies", [])
            days = d.get("days_since_last", 0)
            name = d["contact"].split()[0]
            if "dormant" in anomalies:
                action_fb, msg_fb = "reconnect", f"Hey {name}! It's been ages — how have you been? Would love to catch up soon."
            elif "one_sided" in anomalies:
                action_fb, msg_fb = "check_in", f"Hey {name}, hope you're doing well! Been a while since we properly talked."
            elif "unresolved_plans" in anomalies:
                action_fb, msg_fb = "follow_up_plan", f"Hey {name}, wanted to follow up on those plans we mentioned — still down?"
            elif "frequency_decay" in anomalies:
                action_fb, msg_fb = "send_nudge", f"Hey {name}! Miss talking, what's been going on with you lately?"
            else:
                action_fb, msg_fb = "send_nudge", f"Hey {name}! Just checking in — how are things going?"
            ai = {
                "situation_summary": f"Relationship shows signs of {', '.join(anomalies) if anomalies else 'drift'}. Last contact {days} days ago.",
                "action_type": action_fb,
                "urgency": d.get("priority", "medium"),
                "reasoning": f"Based on {len(anomalies)} detected issue(s) and a health score of {d['health_score']}/100.",
                "draft_message": msg_fb,
                "insight": "Consistent small touchpoints matter more than infrequent long conversations."
            }
        action  = ai.get("action_type","check_in")
        urgency = ai.get("urgency","medium")
        urg_color = "#f87171" if urgency=="high" else "#fbbf24" if urgency=="medium" else "#4ade80"
        st.markdown(f"""
        <div class='action-card'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px'>
                <span style='font-size:1.1rem;font-weight:600;color:#e8e8f0'>{action_icons.get(action,"💬")} {d['contact']}</span>
                <span class='grade-badge grade-{d["grade"]}'>{d["grade"]} · {d["health_score"]}</span>
                <span style='font-size:0.8rem;font-weight:600;color:{urg_color}'>{urgency_map.get(urgency,urgency.upper())}</span>
            </div>
            <div style='color:#94a3b8;font-size:0.88rem;margin-bottom:10px'>{ai.get("situation_summary","")}</div>
            <div style='color:#6b7280;font-size:0.8rem;margin-bottom:8px'><strong style='color:#a78bfa'>Action: {action.replace("_"," ").upper()}</strong> · {ai.get("reasoning","")}</div>
            <div class='draft-message'>"{ai.get("draft_message","")}"</div>
            <div class='insight-box'>💡 {ai.get("insight","")}</div>
        </div>
        """, unsafe_allow_html=True)

# ══ CONVERSATION VIEW ══════════════════════════════════════════════════════════
elif page == "💬 Conversation View":
    st.markdown("<div class='main-title'>Conversation Timeline</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Raw communication patterns per contact</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if chats_df.empty:
        st.warning("No chat data found.")
        st.stop()

    selected = st.selectbox("Select Contact", sorted(chats_df["contact"].unique().tolist()))
    c_data = next((c for c in scored if c["contact"] == selected), None)

    if c_data:
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Health Score", f"{c_data['health_score']}/100")
        m2.metric("Grade", c_data["grade"])
        m3.metric("Days Silent", c_data["days_since_last"])
        m4.metric("Priority", c_data["priority"].upper())

    cdf = chats_df[chats_df["contact"] == selected].sort_values("timestamp")

    st.markdown("<div class='section-header' style='margin-top:20px'>ACTIVITY OVER TIME</div>", unsafe_allow_html=True)
    daily = cdf.set_index("timestamp").resample("D").size().reset_index(name="count")
    fig_act = go.Figure(go.Scatter(
        x=daily["timestamp"], y=daily["count"],
        fill="tozeroy", fillcolor="rgba(167,139,250,0.13)",
        line=dict(color="#a78bfa", width=2), mode="lines",
    ))
    fig_act.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#1f1f2e", tickfont=dict(color="#6b7280")),
        yaxis=dict(gridcolor="#1f1f2e", tickfont=dict(color="#6b7280")),
        margin=dict(l=10,r=10,t=10,b=10), height=180,
    )
    st.plotly_chart(fig_act, use_container_width=True)

    st.markdown("<div class='section-header'>RECENT MESSAGES</div>", unsafe_allow_html=True)
    for _, row in cdf.tail(15).iterrows():
        is_me = row["sender"] == "You"
        bg     = "#1a0f2e" if is_me else "#13131a"
        border = "#a78bfa" if is_me else "#2a2a3e"
        name_c = "#a78bfa" if is_me else "#60a5fa"
        radius = "16px 4px 16px 16px" if is_me else "4px 16px 16px 16px"
        st.markdown(f"""
        <div style='display:flex;justify-content:{"flex-end" if is_me else "flex-start"};margin-bottom:8px'>
            <div style='max-width:65%;background:{bg};border:1px solid {border};border-radius:{radius};padding:10px 14px'>
                <div style='font-size:0.72rem;color:{name_c};margin-bottom:4px;font-weight:600'>{row["sender"]}</div>
                <div style='font-size:0.88rem;color:#e8e8f0'>{row["message"]}</div>
                <div style='font-size:0.68rem;color:#4b5563;margin-top:4px'>{row["timestamp"].strftime("%b %d, %H:%M")}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    dec = next((d for d in decisions if d["contact"] == selected), None)
    if dec and dec.get("ai_decision"):
        ai = dec["ai_decision"]
        st.markdown("<div class='section-header' style='margin-top:20px'>AI RECOMMENDATION</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='action-card'>
            <div style='color:#a78bfa;font-weight:600;margin-bottom:8px'>🤖 {ai.get("action_type","").replace("_"," ").upper()}</div>
            <div style='color:#94a3b8;font-size:0.88rem;margin-bottom:10px'>{ai.get("situation_summary","")}</div>
            <div class='draft-message'>"{ai.get("draft_message","")}"</div>
            <div class='insight-box'>💡 {ai.get("insight","")}</div>
        </div>
        """, unsafe_allow_html=True)