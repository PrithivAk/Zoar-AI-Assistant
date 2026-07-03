"""
Zoar — Multi-Agent Personal AI Assistant
Streamlit demo app: chat interface + mood trend tab + mock interview tab.

Run with: streamlit run app.py
"""
import html as htmlmod

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from orchestrator import route_intent
from agents import wellness_agent, shopping_agent, interview_agent
from db import init_db, log_message, get_chat_history, get_recent_moods

st.set_page_config(page_title="Zoar", page_icon="✦", layout="centered")
init_db()

# ============================================================
# DESIGN TOKENS
# ============================================================
COLORS = {
    "bg": "#12141C",
    "surface": "#1B1E2A",
    "surface_2": "#232739",
    "border": "#2E3346",
    "text": "#EDE8DD",
    "text_dim": "#9BA0B3",
    "amber": "#E8A54B",     # brand / primary accent
    "wellness": "#8FB996",  # sage
    "shopping": "#D98B8B",  # dusty rose
    "interview": "#6C8EBF", # steel blue
    "general": "#8A8FA3",   # slate
}

AGENT_LABELS = {
    "wellness": "Wellness",
    "shopping": "Shopping",
    "interview": "Interview",
    "general": "Zoar",
}

# ============================================================
# GLOBAL CSS — signature: color-coded "agent thread" system.
# Every reply carries a left-border + label in its agent's color,
# and that same color language repeats in the tab rail, the mood
# chart, and the interview card — so which specialist is "speaking"
# is always visually legible, not just stated in text.
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {{
    background-color: {COLORS['bg']};
    color: {COLORS['text']};
    font-family: 'Inter', sans-serif;
}}
[data-testid="stHeader"] {{ background-color: transparent; }}
.block-container {{ padding-top: 2.2rem; max-width: 780px; }}

/* ---------- Title block ---------- */
.zoar-title {{
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 2.6rem;
    letter-spacing: -0.01em;
    margin-bottom: 0.1rem;
    color: {COLORS['text']};
}}
.zoar-title span {{ color: {COLORS['amber']}; }}
.zoar-tagline {{
    color: {COLORS['text_dim']};
    font-size: 0.95rem;
    margin-bottom: 1rem;
}}

/* ---------- Agent legend (signature element) ---------- */
.agent-legend {{
    display: flex;
    gap: 1.1rem;
    flex-wrap: wrap;
    margin-bottom: 1.6rem;
    padding-bottom: 1.3rem;
    border-bottom: 1px solid {COLORS['border']};
}}
.agent-chip {{
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.03em;
    color: {COLORS['text_dim']};
    text-transform: uppercase;
}}
.agent-dot {{
    width: 8px; height: 8px; border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px currentColor;
}}

/* ---------- Tabs styled as a pill rail ---------- */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    background-color: {COLORS['surface']};
    padding: 5px;
    border-radius: 12px;
    border: 1px solid {COLORS['border']};
}}
.stTabs [data-baseweb="tab"] {{
    height: 38px;
    border-radius: 8px;
    color: {COLORS['text_dim']};
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 0.88rem;
    background-color: transparent;
}}
.stTabs [aria-selected="true"] {{
    background-color: {COLORS['surface_2']} !important;
    color: {COLORS['text']} !important;
    box-shadow: inset 0 0 0 1px {COLORS['border']};
}}

/* ---------- Chat message cards ---------- */
.msg-row {{ margin-bottom: 0.9rem; display: flex; flex-direction: column; }}
.msg-meta {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: {COLORS['text_dim']};
    margin-bottom: 0.3rem;
}}
.msg-bubble {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-left: 3px solid {COLORS['general']};
    border-radius: 10px;
    padding: 0.7rem 0.95rem;
    font-size: 0.92rem;
    line-height: 1.5;
    white-space: pre-wrap;
}}
.msg-user .msg-bubble {{
    border-left: 3px solid {COLORS['border']};
    background-color: {COLORS['surface_2']};
}}
.msg-agent-wellness .msg-bubble {{ border-left-color: {COLORS['wellness']}; }}
.msg-agent-shopping .msg-bubble {{ border-left-color: {COLORS['shopping']}; }}
.msg-agent-interview .msg-bubble {{ border-left-color: {COLORS['interview']}; }}
.msg-agent-wellness .msg-meta {{ color: {COLORS['wellness']}; }}
.msg-agent-shopping .msg-meta {{ color: {COLORS['shopping']}; }}
.msg-agent-interview .msg-meta {{ color: {COLORS['interview']}; }}

/* ---------- Buttons ---------- */
.stButton > button {{
    background-color: {COLORS['amber']};
    color: #1A1408;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.85rem;
    padding: 0.5rem 1.1rem;
}}
.stButton > button:hover {{ background-color: #F0B466; color: #1A1408; }}

/* ---------- Inputs ---------- */
[data-testid="stChatInput"], .stTextArea textarea, .stSelectbox > div > div {{
    background-color: {COLORS['surface']} !important;
    border: 1px solid {COLORS['border']} !important;
    color: {COLORS['text']} !important;
    border-radius: 10px !important;
}}

/* ---------- Cards for interview / empty states ---------- */
.zoar-card {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-left: 3px solid {COLORS['interview']};
    border-radius: 10px;
    padding: 1rem 1.1rem;
    margin-bottom: 1rem;
}}
.zoar-card .qlabel {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: {COLORS['interview']};
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.4rem;
}}
.zoar-empty {{
    color: {COLORS['text_dim']};
    font-size: 0.88rem;
    padding: 1.2rem;
    text-align: center;
    border: 1px dashed {COLORS['border']};
    border-radius: 10px;
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
st.markdown('<div class="zoar-title">Zo<span>a</span>r</div>', unsafe_allow_html=True)
st.markdown('<div class="zoar-tagline">One assistant, three specialists — wellness, shopping, interview prep.</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="agent-legend">
    <span class="agent-chip"><span class="agent-dot" style="color:{COLORS['wellness']}; background:{COLORS['wellness']};"></span>Wellness</span>
    <span class="agent-chip"><span class="agent-dot" style="color:{COLORS['shopping']}; background:{COLORS['shopping']};"></span>Shopping</span>
    <span class="agent-chip"><span class="agent-dot" style="color:{COLORS['interview']}; background:{COLORS['interview']};"></span>Interview</span>
    <span class="agent-chip"><span class="agent-dot" style="color:{COLORS['general']}; background:{COLORS['general']};"></span>General</span>
</div>
""", unsafe_allow_html=True)

# ---------- Session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role": "user"/"assistant", "content": str, "agent": str}]
if "interview_transcript" not in st.session_state:
    st.session_state.interview_transcript = []
if "interview_active" not in st.session_state:
    st.session_state.interview_active = False
if "current_question" not in st.session_state:
    st.session_state.current_question = None


def render_message(role: str, content: str, agent: str = "general"):
    css_class = "msg-user" if role == "user" else f"msg-agent-{agent}"
    label = "You" if role == "user" else AGENT_LABELS.get(agent, "Zoar")
    safe_content = htmlmod.escape(content)
    st.markdown(f"""
        <div class="msg-row {css_class}">
            <div class="msg-meta">{label}</div>
            <div class="msg-bubble">{safe_content}</div>
        </div>
    """, unsafe_allow_html=True)


tab_chat, tab_mood, tab_interview = st.tabs(["Chat", "Mood Trend", "Mock Interview"])

# ============================================================
# CHAT TAB
# ============================================================
with tab_chat:
    if not st.session_state.messages:
        st.markdown('<div class="zoar-empty">No messages yet — try "I need running shoes under 3000" or "I\'m feeling stressed about tomorrow".</div>', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        render_message(msg["role"], msg["content"], msg.get("agent", "general"))

    user_input = st.chat_input("Talk to Zoar...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input, "agent": "general"})
        log_message("user", user_input)

        with st.spinner("Routing to the right specialist..."):
            intent = route_intent(user_input)

            if intent == "wellness":
                reply = wellness_agent.handle(user_input)
            elif intent == "shopping":
                reply = shopping_agent.handle(user_input)
            elif intent == "interview":
                reply = interview_agent.handle(user_input)
                st.session_state.interview_active = True
                st.session_state.current_question = reply.split("\n\n")[-1]
            else:
                reply = ("Hey! I'm Zoar — I can help with mood check-ins, "
                         "shopping recommendations, or mock interview practice. "
                         "What would you like to do?")

        st.session_state.messages.append({"role": "assistant", "content": reply, "agent": intent})
        log_message("assistant", reply, agent=intent)
        st.rerun()

# ============================================================
# MOOD TREND TAB
# ============================================================
with tab_mood:
    rows = get_recent_moods(14)
    if rows:
        df = pd.DataFrame([dict(r) for r in rows])
        avg = df["mood_score"].mean()
        low_days = int((df["mood_score"] <= 2).sum())

        c1, c2, c3 = st.columns(3)
        c1.metric("Entries", len(df))
        c2.metric("Average mood", f"{avg:.1f}/5")
        c3.metric("Low days", low_days)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["mood_score"],
            mode="lines+markers",
            line=dict(color=COLORS["wellness"], width=2.5),
            marker=dict(color=COLORS["wellness"], size=7),
        ))
        fig.update_layout(
            paper_bgcolor=COLORS["bg"],
            plot_bgcolor=COLORS["bg"],
            font=dict(color=COLORS["text_dim"], family="Inter"),
            yaxis=dict(range=[0.5, 5.5], gridcolor=COLORS["border"], title="Mood (1-5)"),
            xaxis=dict(gridcolor=COLORS["border"], showgrid=False),
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Raw entries"):
            st.dataframe(df[["date", "mood_score", "note"]], use_container_width=True)
    else:
        st.markdown('<div class="zoar-empty">No mood entries yet. Chat with Zoar about how you\'re feeling to start tracking.</div>', unsafe_allow_html=True)

# ============================================================
# MOCK INTERVIEW TAB
# ============================================================
with tab_interview:
    category = st.selectbox("Question category", ["hr", "behavioral", "technical"])

    if st.button("Start / New Question"):
        st.session_state.current_question = interview_agent.get_random_question(category)
        st.session_state.interview_active = True

    if st.session_state.current_question:
        st.markdown(f"""
            <div class="zoar-card">
                <div class="qlabel">Question</div>
                {htmlmod.escape(st.session_state.current_question)}
            </div>
        """, unsafe_allow_html=True)

        answer = st.text_area("Your answer", key="interview_answer", label_visibility="collapsed",
                               placeholder="Type your answer here...")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Submit answer") and answer.strip():
                st.session_state.interview_transcript.append((st.session_state.current_question, answer))
                with st.spinner("Generating follow-up..."):
                    followup = interview_agent.get_followup(st.session_state.current_question, answer)
                st.session_state.current_question = followup
                st.rerun()
        with col2:
            if st.button("End & get feedback") and st.session_state.interview_transcript:
                with st.spinner("Preparing feedback..."):
                    feedback = interview_agent.get_feedback(st.session_state.interview_transcript)
                st.markdown(f'<div class="zoar-card" style="border-left-color:{COLORS["amber"]};"><div class="qlabel" style="color:{COLORS["amber"]};">Feedback</div>{htmlmod.escape(feedback)}</div>', unsafe_allow_html=True)
                st.session_state.interview_transcript = []
                st.session_state.current_question = None
    else:
        st.markdown('<div class="zoar-empty">Pick a category and hit "Start / New Question" to begin.</div>', unsafe_allow_html=True)

    if st.session_state.interview_transcript:
        with st.expander(f"Transcript ({len(st.session_state.interview_transcript)} Q&A so far)"):
            for q, a in st.session_state.interview_transcript:
                st.markdown(f"**Q:** {q}\n\n**A:** {a}")
