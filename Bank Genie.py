import streamlit as st
import openai
import os
import requests
from PyPDF2 import PdfReader
from langdetect import detect

# Set page config
st.set_page_config(page_title="🏦 Bank Genie", layout="centered")

# Load knowledge base PDF from GitHub
@st.cache_data
def load_knowledge_base():
    url = "https://raw.githubusercontent.com/Superai-cool/Bank-Genie/b2724bae6283a1524d3abcfaf80071961441ec11/bank_knowledge_base.pdf"
    response = requests.get(url)
    with open("temp_kb.pdf", "wb") as f:
        f.write(response.content)
    reader = PdfReader("temp_kb.pdf")
    text = "\n".join(page.extract_text() for page in reader.pages)
    return text

knowledge_base_text = load_knowledge_base()

# Get OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# Refine vague or poorly formed input
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
            temperature=0.3,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except:
        return raw_input

# Build the QA prompt from KB
def build_prompt(refined_query, detail_level, detected_lang):
    style = """
If Short response is requested:
- Summarize the answer in 2–3 lines
- Provide one simple real-life example
- Use Indian context and INR

If Detailed response is requested:
- Explain clearly in 5–6 lines
- Include one proper real-life example
- Use Indian context and INR
"""
    return f"""
You are Bank Genie, an internal AI assistant that answers ONLY using the following corporate banking knowledge base:

=====================
{knowledge_base_text}
=====================

You MUST NOT answer from outside this knowledge base.
If you can't find an answer, say:
"I'm only allowed to answer based on our internal knowledge base, and I couldn't find relevant info for this query."

Instructions:
- Detect the input language and respond in it (e.g., Hindi, Marathi)
- Separate answer and example with a blank line
- Always format answer and example in markdown blocks
- Follow this style:
{style}

Answer in this language: {detected_lang}
Format:
Answer

Example

Question: """{refined_query}"""
"""

# Translate back to original language
def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

# Answer from GPT
def generate_answer():
    raw_input = st.session_state.query.strip()
    if not raw_input:
        st.warning("Please enter a bank-related question.")
        return

    lang = detect_language(raw_input)
    refined_query = refine_query(raw_input)
    st.session_state.query = refined_query

    prompt = build_prompt(refined_query, st.session_state.detail_level, lang)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=600
        )
        full_response = response.choices[0].message.content.strip()
        parts = full_response.split("\n\n", 1)
        st.session_state.answer = parts[0].strip()
        st.session_state.example = parts[1].strip() if len(parts) > 1 else ""
    except Exception as e:
        st.error("Something went wrong: " + str(e))

# Clear session
def clear_all():
    for key in ["query", "detail_level", "answer", "example"]:
        st.session_state.pop(key, None)
    st.rerun()

# Defaults
st.session_state.setdefault("query", "")
st.session_state.setdefault("detail_level", "Short")
st.session_state.setdefault("answer", "")
st.session_state.setdefault("example", "")

# UI
st.markdown("<h1 style='text-align:center;'>🏦 Bank Genie</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;'>🔐 Internal Assistant for Indian Bank Employees | ⚡ Accurate • ⚙️ Instant • 💼 Professional</div><br>", unsafe_allow_html=True)

st.session_state.query = st.text_area("\U0001f50d Ask a bank-related question", value=st.session_state.query, height=130)
st.session_state.detail_level = st.selectbox("\ud83d\udcc3 Choose Answer Format", ["Short", "Detailed"], index=0)

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("💬 Ask Bank Genie"):
        generate_answer()
with col2:
    if st.button("🪓 Clear"):
        clear_all()

# Display output
if st.session_state.answer:
    st.markdown("### 🟢 Answer")
    st.markdown(f"""
    <div style='background-color:#f1f5f9;padding:1rem;border-radius:8px;margin-bottom:1rem;'>
    {st.session_state.answer}
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.example:
        st.markdown(f"""
        <div style='background-color:#e0f2fe;padding:1rem;border-radius:8px;'>
        {st.session_state.example}
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<hr style='margin-top:2rem;'>
<div style='text-align:center;font-size:0.85rem;color:gray;'>
🔐 Built with ❤️ by <strong>SuperAI Labs</strong> — Tailored for Indian Banks 🇮🇳
</div>
""", unsafe_allow_html=True)
