import streamlit as st
import openai
import requests
import PyPDF2
import random
import os
from io import BytesIO
from langdetect import detect

# ✅ Streamlit Page Config
st.set_page_config(page_title="🏦 Bank Genie", layout="centered")

# ✅ OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# ✅ Load Knowledge Base PDF from GitHub
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

pdf_url = "https://raw.githubusercontent.com/Superai-cool/Bank-Genie/b2724bae6283a1524d3abcfaf80071961441ec11/bank_knowledge_base.pdf"
knowledge_base = load_pdf_from_github(pdf_url)

# ✅ Detect and translate Indian language input to English
def maybe_translate_to_english(text):
    try:
        lang = detect(text)
        if lang != "en":
            translation_prompt = f"Translate this banking question to English:\n\n{text}"
            result = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": translation_prompt}],
                temperature=0.2,
                max_tokens=100
            )
            translated = result['choices'][0]['message']['content'].strip()
            return translated, lang
        return text, "en"
    except Exception:
        return text, "en"

# ✅ Translate response back to user's language
def maybe_translate_back_to_original(answer_text, target_lang):
    if target_lang == "en":
        return answer_text
    try:
        prompt = f"Translate the following banking answer to {target_lang}:\n\n{answer_text}"
        result = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600
        )
        return result['choices'][0]['message']['content'].strip()
    except Exception:
        return answer_text

# ✅ Refine vague input
def refine_query(raw_input):
    prompt = f"""
You are a helper that improves vague or poorly written banking queries.

Input:
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
    except Exception:
        return raw_input

# ✅ Build Prompt
def build_prompt(refined_query, detail_level, lang_code):
    return f"""
You are Bank Genie, an AI assistant for bank employees.

ONLY use the content from the knowledge base below to answer.
If no answer is found, reply:
"I'm only allowed to answer based on our internal knowledge base, and I couldn’t find relevant info for this query."

📘 Knowledge Base:
\"\"\"{knowledge_base}\"\"\"

📝 Format: {"Short answer (1–3 lines) with example" if detail_level == "Short" else "Detailed explanation (5–6 lines) with example"}

🗣️ Respond in the same language as: {lang_code}
Use Indian examples and INR. Show answer and example in 2 separate paragraphs.

QUESTION:
\"\"\"{refined_query}\"\"\"
"""

# ✅ Generate GPT Answer
def generate_answer():
    raw_input = st.session_state.query.strip()
    if not raw_input:
        st.warning("Please enter a bank-related question.")
        return

    translated_query, lang_code = maybe_translate_to_english(raw_input)
    refined_query = refine_query(translated_query)

    st.session_state.lang_code = lang_code
    st.session_state.query = raw_input

    prompt = build_prompt(refined_query, st.session_state.detail_level, lang_code)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600
        )
        english_answer = response['choices'][0]['message']['content'].strip()

        # 🔁 Translate full answer to original language if needed
        translated_back = maybe_translate_back_to_original(english_answer, lang_code)
        st.session_state.answer = translated_back

    except Exception as e:
        st.error(f"Error: {e}")

# ✅ Clear All
def clear_all():
    for key in ["query", "answer", "detail_level", "lang_code"]:
        st.session_state.pop(key, None)
    st.rerun()

# ✅ Session State Defaults
st.session_state.setdefault("query", "")
st.session_state.setdefault("answer", "")
st.session_state.setdefault("detail_level", "Short")
st.session_state.setdefault("lang_code", "en")

# ✅ UI
st.markdown("## 🏦 Bank Genie")
st.markdown("🔐 Internal Assistant for Indian Bank Employees | ⚡ Accurate • ⚙️ Instant • 💼 Professional")

st.text_area("🔍 Ask a bank-related question", key="query", height=120)
st.selectbox("📏 Choose Answer Format", ["Short", "Detailed"], key="detail_level")

col1, col2 = st.columns(2)
with col1:
    if st.button("💬 Ask Bank Genie"):
        generate_answer()
with col2:
    if st.button("🧹 Clear"):
        clear_all()

# ✅ Display Answer + Example
if st.session_state.answer:
    st.markdown("### ✅ Answer")

    # Try splitting using known indicators
    indicators = ["For example", "उदाहरणार्थ", "उदाहरण", "उदा.", "उदाहरण:", "उदाहरणासारखे"]
    split_index = -1
    for marker in indicators:
        idx = st.session_state.answer.find(marker)
        if idx != -1:
            split_index = idx
            break

    if split_index != -1:
        ans = st.session_state.answer[:split_index].strip()
        ex = st.session_state.answer[split_index:].strip()
    else:
        ans, ex = st.session_state.answer.strip(), ""

    st.markdown(f"""
    <div style='background-color:#f3f4f6; padding: 1rem; border-radius: 10px;
                border: 1px solid #d1d5db; font-size: 1rem; margin-bottom: 1rem;'>
        {ans}
    </div>
    """, unsafe_allow_html=True)

    if ex:
        st.markdown(f"""
        <div style='background-color:#eef2ff; padding: 1rem; border-radius: 10px;
                    border: 1px solid #c7d2fe; font-size: 1rem;'>
            {ex}
        </div>
        """, unsafe_allow_html=True)

# ✅ Footer
st.markdown("""
    <hr>
    <div style='text-align: center; font-size: 0.85rem; color: gray;'>
        🔐 Built with ❤️ by <strong>SuperAI Labs</strong> — Tailored for Indian Banks 🇮🇳
    </div>
""", unsafe_allow_html=True)
