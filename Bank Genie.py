import streamlit as st
import openai
import os
import requests
import PyPDF2
from langdetect import detect
from io import BytesIO

# ✅ Page Config
st.set_page_config(page_title="🏦 Bank Genie", layout="centered")

# ✅ Load PDF from GitHub
@st.cache_data(show_spinner=False)
def load_pdf_from_github():
    url = "https://raw.githubusercontent.com/Superai-cool/Bank-Genie/b2724bae6283a1524d3abcfaf80071961441ec11/bank_knowledge_base.pdf"
    response = requests.get(url)
    with BytesIO(response.content) as file:
        reader = PyPDF2.PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

knowledge_base = load_pdf_from_github()

# ✅ Styles
st.markdown("""
<style>
html, body, [class*="css"]  { font-family: 'Segoe UI', sans-serif; }
textarea { min-height: 130px !important; }
.button-row { display: flex; gap: 1rem; margin-top: 1.5rem; }
.stButton > button { border-radius: 6px; padding: 0.6rem 1.5rem; font-weight: 600; }
.stButton > button:hover { transform: scale(1.02); }
@media (max-width: 600px) { .button-row { flex-direction: column; } }
</style>
""", unsafe_allow_html=True)

# ✅ OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# ✅ Build Prompt
def build_prompt(refined_query, detail_level):
    return f"""
You are Bank Genie, an AI assistant designed for Indian bank employees. Use only the internal PDF knowledge base below to answer.

Knowledge Base:
"""
{knowledge_base}
"""

Instructions:
- If Short format is selected: Give a 2–3 line answer + 1 real-life example (in INR)
- If Detailed: Give a longer answer (5–6 lines) + 1 real-life example (in INR)
- Detect question language and answer in same
- Keep answer and example clearly separated

Question: {refined_query}
"""

# ✅ Translate language
def detect_lang(text):
    try:
        return detect(text)
    except:
        return "en"

# ✅ Generate Answer
def generate_answer():
    raw_input = st.session_state.query.strip()
    if not raw_input:
        st.warning("Please enter a question.")
        return

    lang = detect_lang(raw_input)
    refined_query = raw_input if raw_input.endswith("?") else f"What is {raw_input}?"
    st.session_state.query = refined_query

    prompt = build_prompt(refined_query, st.session_state.detail_level)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        result = response.choices[0].message.content.strip()

        if "\n\n" in result:
            answer, example = result.split("\n\n", 1)
        else:
            answer, example = result, ""

        st.session_state.answer = answer.strip()
        st.session_state.example = example.strip()

    except Exception as e:
        st.error("Failed to generate answer.")
        st.exception(e)

# ✅ Clear
def clear_all():
    for key in ["query", "answer", "example"]:
        st.session_state.pop(key, None)
    st.rerun()

# ✅ Session State Defaults
st.session_state.setdefault("query", "")
st.session_state.setdefault("detail_level", "Short")
st.session_state.setdefault("answer", "")
st.session_state.setdefault("example", "")

# ✅ UI Layout
st.title("🏦 Bank Genie")
st.markdown("""
#### 🔐 Internal Assistant for Indian Bank Employees | ⚡ Accurate • ⚙️ Instant • 💼 Professional
""")

st.text_area("🔍 Ask a bank-related question", key="query")
st.selectbox("✏️ Choose Answer Format", ["Short", "Detailed"], key="detail_level")

with st.container():
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("💬 Ask Bank Genie"):
            generate_answer()
    with col2:
        if st.button("🧹 Clear"):
            clear_all()

# ✅ Output
if st.session_state.answer:
    st.markdown("### ✅ Answer")
    st.markdown(f"""
    <div style='background-color:#f1f5f9;padding:1rem;border-radius:8px;border:1px solid #cbd5e1;'>
    {st.session_state.answer}
    </div>
    """, unsafe_allow_html=True)

if st.session_state.example:
    st.markdown(f"""
    <div style='background-color:#eef2ff;padding:1rem;margin-top:1rem;border-radius:8px;border:1px solid #c7d2fe;'>
    {st.session_state.example}
    </div>
    """, unsafe_allow_html=True)

# ✅ Footer
st.markdown("""
---
<div style='text-align:center;font-size:0.9rem;color:gray;'>
🔐 Built with ❤️ by <strong>SuperAI Labs</strong> — Tailored for Indian Banks 🇮🇳
</div>
""", unsafe_allow_html=True)
