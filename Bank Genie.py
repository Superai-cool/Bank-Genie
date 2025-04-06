import streamlit as st
import openai
import os
import random

# ✅ Set Page Config
st.set_page_config(page_title="🏦 Bank Genie", layout="centered")

# ✅ Global Styles
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #f4f4f5;
    }
    .main, .block-container { padding-top: 1rem !important; }
    .container {
        background-color: white;
        padding: 2rem 1.5rem;
        max-width: 700px;
        margin: auto;
        border-radius: 10px;
    }
    .title { text-align: center; font-size: 2rem; font-weight: 600; color: #1e3a8a; margin-bottom: 0.25rem; }
    .subtitle { text-align: center; font-size: 1rem; color: #52525b; margin-bottom: 1.5rem; }
    textarea {
        height: 100px !important;
        padding: 12px !important;
        border: 1.5px solid #d1d5db !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
        resize: none !important;
        background-color: #ffffff !important;
        color: #111827 !important;
    }
    textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
        outline: none !important;
    }
    .button-row {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
    }
    .stButton > button {
        font-size: 1rem !important;
        padding: 0.65rem 1.2rem !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        background-color: #000000 !important;
        color: white !important;
        border: none !important;
        transition: all 0.15s ease-in-out;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stButton > button:hover {
        background-color: #111111 !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .stButton > button:active {
        transform: scale(0.98);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
    }
    @media (max-width: 600px) {
        .button-row { flex-direction: column; }
    }
    </style>
""", unsafe_allow_html=True)

# ✅ OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# ✅ Auto-fix: Single-word and grammar
def refine_query(raw_input):
    prompt = f"""
You are a helper that converts vague or poorly written banking queries into clear questions.

If the input is:
- A single banking word like "loan" → expand into a proper question.
- Grammatically incorrect or unclear → fix it.
- Already good → return as is.

INPUT:
\"\"\"{raw_input}\"\"\"

Rewritten Question:
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=100
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Error refining question: {e}")
        return raw_input

# ✅ Build Bank Genie Prompt
def build_prompt(refined_query, detail_level):
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

✅ For valid banking questions:
{detail_addon}

🌐 Universal Instructions:
- Keep answer and example on separate lines with space between
- Answer in the same language the user asked

QUERY:
\"\"\"{refined_query}\"\"\"
"""

# ✅ Generate Answer
def generate_answer():
    raw_input = st.session_state.query.strip()
    if not raw_input:
        st.warning("Please enter a bank-related question.")
        return

    refined_query = refine_query(raw_input)
    st.session_state.query = refined_query

    prompt = build_prompt(refined_query, st.session_state.detail_level)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=random.uniform(0.4, 0.7),
            max_tokens=400
        )
        st.session_state.answer = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Error generating answer: {e}")

# ✅ Clear All
def clear_all():
    for key in ["query", "detail_level", "answer"]:
        st.session_state.pop(key, None)
    st.rerun()

# ✅ Session Defaults
st.session_state.setdefault("query", "")
st.session_state.setdefault("detail_level", "Short")
st.session_state.setdefault("answer", "")

# ✅ App UI
st.markdown("<div class='container'>", unsafe_allow_html=True)
st.markdown("<div class='title'>🏦 Bank Genie</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Internal assistant for Indian bank employees. Accurate. Instant. Professional.</div>", unsafe_allow_html=True)

st.session_state.query = st.text_area("🔍 Ask a bank-related question", value=st.session_state.query, height=130)
st.session_state.detail_level = st.selectbox("📏 Choose Answer Format", ["Short", "Detailed"], index=0)

# ✅ Action Buttons
st.markdown("<div class='button-row'>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    if st.button("💬 Ask Bank Genie"):
        generate_answer()
with col2:
    if st.button("🧹 Clear"):
        clear_all()
st.markdown("</div>", unsafe_allow_html=True)

# ✅ Output: Answer + Example
if st.session_state.answer:
    st.markdown("### 🧾 Answer")

    parts = st.session_state.answer.strip().split("\n\n", 1)
    main_answer = parts[0]
    example_part = parts[1] if len(parts) > 1 else ""

    st.markdown(f"""
    <div style='background-color:#f9fafb; border:1px solid #e5e7eb; padding: 1.25rem; border-radius: 10px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.06); font-size: 1rem; margin-bottom: 1.2rem;'>
        {main_answer}
    </div>
    """, unsafe_allow_html=True)

    if example_part:
        st.markdown(f"""
        <div style='background-color:#eef2ff; border:1px solid #c7d2fe; padding: 1.25rem; border-radius: 10px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.05); font-size: 1rem;'>
            {example_part}
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ✅ Footer
st.markdown("""
    <hr style='margin-top: 3rem;'>
    <div style='text-align: center; font-size: 0.85rem; color: #6b7280;'>
        🔐 Built with ❤️ by <strong>SuperAI Labs</strong> — Tailored for Indian Banks 🇮🇳
    </div>
""", unsafe_allow_html=True)
