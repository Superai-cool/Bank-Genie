import streamlit as st
import openai
import os
import random

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# Streamlit Page Config
st.set_page_config(page_title="🏦 Bank Genie", layout="centered", initial_sidebar_state="collapsed")

# 🔥 Global Style Overrides - Mobile-First & Floating Buttons
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }
        body {
            background-color: #f0f4f8;
        }

        .main-container {
            max-width: 640px;
            margin: auto;
            padding: 1rem;
            background: white;
            border-radius: 18px;
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.06);
        }

        h1 {
            text-align: center;
            font-size: 2rem;
            color: #1e3a8a;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            text-align: center;
            color: #475569;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }

        .response-box {
            background-color: #f9fafb;
            padding: 1.25rem;
            border-radius: 12px;
            font-size: 1rem;
            line-height: 1.6;
            margin-top: 1.5rem;
            border: 1px solid #e2e8f0;
        }

        .floating-buttons {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-top: 2rem;
            flex-direction: column;
        }

        .floating-buttons button {
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 10px;
            border: none;
            width: 100%;
        }

        .generate-btn {
            background-color: #1d4ed8 !important;
            color: white !important;
        }

        .clear-btn {
            background-color: #dc2626 !important;
            color: white !important;
        }

        @media (min-width: 600px) {
            .floating-buttons {
                flex-direction: row;
            }
            .floating-buttons button {
                width: auto;
            }
        }
    </style>
""", unsafe_allow_html=True)

# 🔄 Session State Defaults
st.session_state.setdefault("query", "")
st.session_state.setdefault("detail_level", "Short")
st.session_state.setdefault("language", "English")
st.session_state.setdefault("answer", "")

# 🧠 Prompt Builder
def build_prompt(query, detail_level, lang):
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
- Answer in the same language the user asked (language: {lang})

QUERY:
\"\"\"{query}\"\"\"
"""

# 🧠 Answer Generator
def generate_answer():
    prompt = build_prompt(st.session_state.query, st.session_state.detail_level, st.session_state.language)
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

# 🧼 Clear
def clear_app():
    for key in ["query", "detail_level", "language", "answer"]:
        st.session_state.pop(key, None)
    st.rerun()

# 🌟 UI Components
with st.container():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    st.markdown("<h1>🏦 Bank Genie</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Smart Q&A assistant for Indian banking staff. Multilingual. Instant. Accurate.</div>", unsafe_allow_html=True)

    st.session_state.query = st.text_area("🔍 Ask a bank-related question", value=st.session_state.query, height=120)

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.detail_level = st.radio("📏 Answer Format", ["Short", "Detailed"], index=["Short", "Detailed"].index(st.session_state.detail_level))
    with col2:
        st.session_state.language = st.selectbox("🌐 Language", ["English", "Hindi", "Marathi", "Kannada", "Tamil"], index=0)

    # 🔘 Buttons: Generate + Clear
    st.markdown("<div class='floating-buttons'>", unsafe_allow_html=True)
    colA, colB = st.columns(2)
    with colA:
        if st.button("💡 Generate Answer", type="primary"):
            if st.session_state.query.strip():
                generate_answer()
            else:
                st.warning("Please enter a bank-related question.")
    with colB:
        if st.button("🧹 Clear"):
            clear_app()
    st.markdown("</div>", unsafe_allow_html=True)

    # ✅ Answer Output
    if st.session_state.answer:
        st.markdown("### ✅ Suggested Answer")
        st.markdown(f"<div class='response-box'>{st.session_state.answer}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# 👣 Footer
st.markdown("""
    <hr style='margin-top: 2.5rem;'>
    <div style='text-align: center; font-size: 0.85rem; color: #6b7280;'>
        🔐 Powered by <strong>SuperAI Labs</strong> • Tailored for Indian Banks 🇮🇳
    </div>
""", unsafe_allow_html=True)
