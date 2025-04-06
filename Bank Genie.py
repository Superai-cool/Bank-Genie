import streamlit as st
import openai
import requests
import PyPDF2
import random
import os
from io import BytesIO
from langdetect import detect

# Page Config
st.set_page_config(page_title="🏦 Bank Genie", layout="centered")

# OpenAI Key
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# Load PDF from GitHub
@st.cache_data
def load_pdf_from_github(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code != 200:
        st.error("❌ Could not load the knowledge base PDF.")
        return ""
    reader = PyPDF2.PdfReader(BytesIO(response.content))
    return "\n".join([page.extract_text() for page in reader.pages])

pdf_url = "https://raw.githubusercontent.com/Superai-cool/Bank-Genie/b2724bae6283a1524d3abcfaf80071961441ec11/bank_knowledge_base.pdf"
knowledge_base = load_pdf_from_github(pdf_url)

# Translation functions
def maybe_translate_to_english(text):
    try:
        lang = detect(text)
        if lang != "en":
            prompt = f"Translate this banking question to English:\n\n{text}"
            result = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100
            )
            return result.choices[0].message.content.strip(), lang
        return text, "en"
    except:
        return text, "en"

def maybe_translate_back_to_original(answer_text, lang_code):
    if lang_code == "en":
        return answer_text
    try:
        prompt = f"Translate the following banking answer to {lang_code}:\n\n{answer_text}"
        result = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=600
        )
        return result.choices[0].message.content.strip()
    except:
        return answer_text

# Refine input
def refine_query(raw_input):
    prompt = f"""
You are a helper that improves vague or poorly written banking queries.

Input:
"""{raw_input}"""

Rewritten Question:
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except:
        return raw_input

# Build Prompt
def build_prompt(refined_query, detail_level, lang_code):
    return f"""
You are Bank Genie, an AI assistant for bank employees.

ONLY use the content from the knowledge base below to answer.
If no answer is found, say:
"I'm only allowed to answer based on our internal knowledge base, and I couldn’t find relevant info for this query."

📘 Knowledge Base:
"""{knowledge_base}"""

📝 Format: {"Short summary (1–3 lines) with one Indian example" if detail_level == "Short" else "Detailed explanation (5–6 lines) with example"}

🗣️ Respond in the same language as this code: {lang_code}
Use Indian context and INR. Separate answer and example with a blank line.

QUESTION:
"""{refined_query}"""
"""

# Generate Answer
def generate_answer():
    raw_input = st.session_state.query.strip()
    if not raw_input:
        st.warning("Please enter a bank-related question.")
        return

    translated_query, lang_code = maybe_translate_to_english(raw_input)
    refined_query = refine_query(translated_query)
    st.session_state.lang_code = lang_code

    prompt = build_prompt(refined_query, st.session_state.detail_level, lang_code)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=random.uniform(0.4, 0.7),
            max_tokens=600
        )
        english_answer = response.choices[0].message.content.strip()
        translated_final = maybe_translate_back_to_original(english_answer, lang_code)
        st.session_state.answer = translated_final
    except Exception as e:
        st.error(f"Error: {e}")

# Clear
def clear_all():
    for k in ["query", "answer", "detail_level", "lang_code"]:
        st.session_state.pop(k, None)
    st.rerun()

# Defaults
st.session_state.setdefault("query", "")
st.session_state.setdefault("answer", "")
st.session_state.setdefault("detail_level", "Short")
st.session_state.setdefault("lang_code", "en")

# UI Layout
st.markdown("## 🏦 Bank Genie")
st.markdown("🔐 Internal Assistant for Indian Bank Employees | ⚡ Accurate • ⚙️ Instant • 💼 Professional")

st.text_area(" 🔍 Ask a bank-related question", key="query", height=130)
st.selectbox(" 📏 Choose Answer Format", ["Short", "Detailed"], key="detail_level")

col1, col2 = st.columns(2)
with col1:
    if st.button("💬 Ask Bank Genie"):
        generate_answer()
with col2:
    if st.button("🧹 Clear"):
        clear_all()

# Output
if st.session_state.answer:
    st.markdown("### ✅ Answer")

    full_text = st.session_state.answer.strip()

    # Split on known markers
    split_point = -1
    markers = ["Example:", "उदाहरणार्थ", "उदाहरण:", "उदा.", "उदाहरणासारखे"]
    for marker in markers:
        if marker in full_text:
            split_point = full_text.find(marker)
            break

    if split_point != -1:
        main_answer = full_text[:split_point].strip()
        example_part = full_text[split_point:].strip()
    else:
        main_answer = full_text
        example_part = ""

    # Answer Box
    st.markdown("""
    <div style='font-weight:600; margin-bottom: 0.25rem;'>📘 Answer</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background-color:#f3f4f6; border:1px solid #d1d5db; padding:1rem; border-radius:10px;
                font-size:1rem; margin-bottom:1.2rem;'>
        {main_answer}
    </div>
    """, unsafe_allow_html=True)

    # Example Box
    if example_part:
        st.markdown("""
        <div style='font-weight:600; margin-bottom: 0.25rem;'>📌 Example</div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background-color:#eef2ff; border:1px solid #c7d2fe; padding:1rem; border-radius:10px;
                    font-size:1rem;'>
            {example_part}
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<hr>
<div style='text-align:center;font-size:0.85rem;color:gray'>
🔐 Built with ❤️ by <strong>SuperAI Labs</strong> — Tailored for Indian Banks 🇮🇳
</div>
""", unsafe_allow_html=True)
