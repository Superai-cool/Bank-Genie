import streamlit as st
import openai
import requests
import PyPDF2
import random
import os
from io import BytesIO

# ✅ Page Config
st.set_page_config(page_title="🏦 Bank Genie", layout="centered")

# ✅ Styles
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
    .title {
        text-align: center;
        font-size: 2rem;
        font-weight: 600;
        color: #1e3a8a;
        margin-bottom: 0.25rem;
    }
    .subtitle {
        font-size: 1rem;
        color: #52525b;
        margin-bottom: 1.5rem;
        text-align: center;
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

# ✅ API Key Setup
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# ✅ Load PDF from GitHub
@st.cache_data
def load_pdf_from_github(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code != 200:
        st.error("❌ Could not load the knowledge base PDF.")
        return ""
    pdf_content = BytesIO(response.content)
    reader = PyPDF2.PdfReader(pdf_content)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# ✅ GitHub Raw PDF URL
pdf_url = "https://raw.githubusercontent.com/Superai-cool/Bank-Genie/b2724bae6283a1524d3abcfaf80071961441ec11/bank_knowledge_base.pdf"
knowledge_base = load_pdf_from_github(pdf_url)

# ✅ Refine Query
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

# ✅ Build GPT Prompt
def build_prompt(refined_query):
    detail = st.session_state.get("detail_level", "Short")
    return f"""
You are Bank Genie, an AI assistant for bank employees. 
Only answer using the official knowledge base provided below. 
If the answer is not found, say:
"I'm only allowed to answer based on our internal knowledge base, and I couldn’t find relevant info for this query."

📘 Knowledge Base:
\"\"\"{knowledge_base}\"\"\"

📝 Response Style: {"Keep it short (1–3 lines) and include a simple Indian example with INR." if detail == "Short" else "Give a detailed explanation (up to 6 lines) and include a real-world Indian example with INR."}

❓ Question:
\"\"\"{refined_query}\"\"\"

🧠 Answer:
"""

# ✅ Generate Answer
def generate_answer():
    raw_input = st.session_state.query.strip()
    if not raw_input:
        st.warning("Please enter a bank-related question.")
        return
    refined_query = refine_query(raw_input)
    st.session_state.query = refined_query

    prompt = build_prompt(refined_query)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        st.session_state.answer = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Error generating answer: {e}")

# ✅ Clear All
def clear_all():
    for key in ["query", "answer", "detail_level"]:
        st.session_state.pop(key, None)
    st.rerun()

# ✅ Session Defaults
st.session_state.setdefault("query", "")
st.session_state.setdefault("answer", "")
st.session_state.setdefault("detail_level", "Short")

# ✅ Layout
st.markdown("<div class='container'>", unsafe_allow_html=True)
st.markdown("<div class='title'>🏦 Bank Genie</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>🔐 Internal Assistant for Indian Bank Employees | ⚡ Accurate • ⚙️ Instant • 💼 Professional</div>", unsafe_allow_html=True)

# ✅ Input
st.session_state.query = st.text_area("🔍 Ask a bank-related question", value=st.session_state.query, height=130)

# ✅ Dropdown
st.session_state.detail_level = st.selectbox("📏 Choose Answer Format", ["Short", "Detailed"], index=0)

# ✅ Buttons
st.markdown("<div class='button-row'>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    if st.button("💬 Ask Bank Genie"):
        generate_answer()
with col2:
    if st.button("🧹 Clear"):
        clear_all()
st.markdown("</div>", unsafe_allow_html=True)

# ✅ Output Split (Answer + Example)
if st.session_state.answer:
    st.markdown("### ✅ Answer")

    parts = st.session_state.answer.strip().split("\n\n", 1)
    main_answer = parts[0]
    example_part = parts[1] if len(parts) > 1 else ""

    # Main Answer Box
    st.markdown(f"""
    <div style='background-color:#f9fafb; border:1px solid #e5e7eb; padding: 1.25rem; border-radius: 10px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.06); font-size: 1rem; margin-bottom: 1.2rem;'>
        {main_answer}
    </div>
    """, unsafe_allow_html=True)

    # Example Box
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
