import streamlit as st
import openai
import os
import random

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# Streamlit App Config
st.set_page_config(page_title="🏦 Bank Genie", layout="centered")

# ✅ Open Graph Meta Tags
st.markdown("""
    <head>
        <meta property="og:title" content="Bank Genie - Internal Banking Q&A Assistant" />
        <meta property="og:description" content="Ask internal banking questions in your preferred language and get context-rich answers tailored for Indian banking." />
        <meta property="og:image" content="https://yourdomain.com/bankgenie-preview.png" />
    </head>
""", unsafe_allow_html=True)

# ✅ Global Styles
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif !important;
        }
        body {
            background-color: #f8fafc;
        }
        .block-container {
            max-width: 720px;
            margin: auto;
            padding-top: 2rem;
        }
        h1 {
            text-align: center;
            color: #1e293b;
            font-size: 2.5rem;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            text-align: center;
            color: #475569;
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
        }
        .response-box {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            font-size: 1.05rem;
            line-height: 1.6;
            white-space: pre-wrap;
            margin-top: 1rem;
        }
        .btn-row {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 1.25rem;
        }
        .btn-row button {
            width: 100%;
            flex: 1;
            padding: 0.7rem;
            font-size: 1rem;
            border-radius: 8px;
            border: none;
            color: white;
        }
        .generate-btn {
            background-color: #0284c7;
        }
        .clear-btn {
            background-color: #dc2626;
        }
    </style>
""", unsafe_allow_html=True)

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

# 🚀 Generate Answer
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

# 🧼 Clear App
def clear_app():
    for key in ["query", "detail_level", "language", "answer"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# 🔄 Session Defaults
st.session_state.setdefault("query", "")
st.session_state.setdefault("detail_level", "Short")
st.session_state.setdefault("language", "English")
st.session_state.setdefault("answer", "")

# 💬 Title + Subtitle
st.markdown("<h1>🏦 Bank Genie</h1>", unsafe_allow_html=True)
st.markdown("""
<div class='subtitle'>
Your internal AI assistant for quick, context-aware responses to banking questions.<br>
Available in English, Hindi, Marathi & more.
</div>
""", unsafe_allow_html=True)

# 📝 Query Input
st.session_state.query = st.text_area("🔍 Enter your bank-related question", value=st.session_state.query, height=130)

# 🎯 Options
col1, col2 = st.columns(2)
with col1:
    st.session_state.detail_level = st.radio("📏 Answer Detail", ["Short", "Detailed"], index=["Short", "Detailed"].index(st.session_state.detail_level))
with col2:
    st.session_state.language = st.selectbox("🌐 Preferred Language", ["English", "Hindi", "Marathi", "Kannada", "Tamil"], index=0)

# 🚦 Action Buttons
st.markdown('<div class="btn-row">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    if st.button("💡 Generate Answer", key="gen"):
        if st.session_state.query.strip():
            generate_answer()
        else:
            st.warning("Please enter a valid banking question.")
with c2:
    if st.button("🧹 Clear", key="clear"):
        clear_app()
st.markdown('</div>', unsafe_allow_html=True)

# ✅ Show Answer
if st.session_state.answer:
    st.markdown("### ✅ Suggested Answer")
    st.markdown(f"<div class='response-box'>{st.session_state.answer}</div>", unsafe_allow_html=True)

# 🌟 Footer
st.markdown("""
<hr style='margin-top: 3rem; margin-bottom: 1rem;'>
<div style='text-align: center; font-size: 0.9rem; color: #6b7280;'>
🔐 Built with ❤️ by <strong>SuperAI Labs</strong> — Banking Knowledge, AI-Powered.
</div>
""", unsafe_allow_html=True)
