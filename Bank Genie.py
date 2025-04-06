import streamlit as st
import openai
import os
import random

# API Key
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# Streamlit Config
st.set_page_config(page_title="🏦 Bank Genie", layout="centered")

# 🧠 Prompt Template
def build_prompt(query, detail_level):
    detail_addon = {
        "Short": "- Give a short, summarized answer (1–3 lines)\n- Include 1 simple real-life example (use Indian context and INR)",
        "Detailed": "- Give a clear, helpful answer (up to 5–6 lines)\n- Include 1 proper real-life example with Indian context and INR"
    }[detail_level]

    return f"""
You are Bank Genie — an internal assistant for bank employees only. You answer only bank-related queries like:
- Account opening/closure, KYC, dormant accounts
- Deposits, withdrawals, cash handling rules
- NEFT, RTGS, UPI, IMPS, cheque handling
- Loans, documentation, eligibility
- Internal tools like Finacle or CBS
- Internal policies, RBI guidelines, audits
- Staff-related questions only if tied to internal policies

❌ Do NOT answer anything unrelated to banking. Respond with:
"I’m designed to answer only internal bank-related questions. Please ask something related to banking."

✅ For valid banking questions:
{detail_addon}

🌐 Universal Instructions:
- Keep answer and example on separate lines with space between
- Avoid repeating the word 'Example' if already used
- Answer in the same language the user asked

QUERY:
\"\"\"{query}\"\"\"
"""

# 🤖 Generate Answer
def generate_answer():
    prompt = build_prompt(st.session_state.query, st.session_state.detail_level)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=random.uniform(0.4, 0.7),
            max_tokens=400
        )
        st.session_state.answer = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Error: {e}")
        st.session_state.answer = ""

# 🧹 Clear
def clear_all():
    for key in ["query", "detail_level", "answer"]:
        st.session_state.pop(key, None)
    st.rerun()

# 🎯 Session Defaults
st.session_state.setdefault("query", "")
st.session_state.setdefault("detail_level", "Short")
st.session_state.setdefault("answer", "")

# ✨ Modern App CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #f1f5f9;
    }

    .card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        max-width: 640px;
        margin: 2rem auto;
        box-shadow: 0 12px 32px rgba(0,0,0,0.05);
    }

    .title {
        text-align: center;
        font-size: 2rem;
        font-weight: 600;
        color: #1e40af;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        text-align: center;
        color: #475569;
        font-size: 1rem;
        margin-bottom: 1.8rem;
    }

    .response-box {
        background-color: #f9fafb;
        padding: 1.25rem;
        border-radius: 12px;
        font-size: 1rem;
        line-height: 1.6;
        margin-top: 1.5rem;
        border: 1px solid #e2e8f0;
        white-space: pre-wrap;
    }

    .button-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-top: 2rem;
    }

    .stButton>button {
        width: 100%;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 10px;
        border: none;
    }

    .stButton>button:first-child {
        background-color: #2563eb;
        color: white;
    }

    .stButton>button:last-child {
        background-color: #f43f5e;
        color: white;
    }

    @media (min-width: 600px) {
        .button-container {
            flex-direction: row;
        }
        .stButton>button {
            width: auto;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ✅ App UI
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    st.markdown("<div class='title'>🏦 Bank Genie</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Smart Q&A assistant for Indian banking staff. Multilingual. Instant. Accurate.</div>", unsafe_allow_html=True)

    st.session_state.query = st.text_area("🔍 Ask a bank-related question", value=st.session_state.query, height=130)

    st.session_state.detail_level = st.radio("📏 Choose Answer Format", ["Short", "Detailed"], horizontal=True)

    # 🚦 Action Buttons
    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💡 Generate Answer"):
            if st.session_state.query.strip():
                generate_answer()
            else:
                st.warning("Please enter a bank-related question.")
    with col2:
        if st.button("🧹 Clear"):
            clear_all()
    st.markdown("</div>", unsafe_allow_html=True)

    # ✅ Display Answer
    if st.session_state.answer:
        st.markdown("### ✅ Suggested Answer")
        st.markdown(f"<div class='response-box'>{st.session_state.answer}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# 🌟 Footer
st.markdown("""
    <hr style="margin-top: 3rem;">
    <div style='text-align: center; font-size: 0.9rem; color: #6b7280;'>
        🔐 Built with ❤️ by <strong>SuperAI Labs</strong> — Tailored for Indian Banks 🇮🇳
    </div>
""", unsafe_allow_html=True)
