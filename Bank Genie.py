import streamlit as st
import openai
import os
from langdetect import detect

# ------------------ Config ------------------
st.set_page_config(page_title="Bank Genie - Internal Assistant", layout="centered")
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OpenAI API key not found.")
    st.stop()
openai.api_key = api_key

# ------------------ App State ------------------
if "response" not in st.session_state:
    st.session_state.response = None

# ------------------ Clear Function ------------------
def clear_all():
    st.session_state.response = None
    st.session_state["query_input"] = ""
    st.session_state["detail_select"] = "Short"
    st.experimental_rerun()

# ------------------ Layout ------------------
st.title("🏦 Bank Genie - Internal Q&A Assistant")
st.markdown("""
👋 Welcome to **Bank Genie** — Empowering Bank Teams with Instant, Multilingual Support.

💬 Ask any bank-related question below, and Bank Genie will provide accurate, helpful answers tailored to your preference — whether concise or in-depth.
""")

# ------------------ Prompt Setup ------------------
def build_prompt(detail_level):
    base = """
You are Bank Genie — an internal assistant for bank employees only. Only respond to valid bank-related queries.

❌ If not related to banking, respond: "I’m designed to answer only internal bank-related questions. Please ask something related to banking."

✅ Otherwise:
"""
    if detail_level == "Short":
        base += "- Short answer (1–3 lines) with 1 INR-based example.\n"
    else:
        base += "- Detailed answer (up to 6 lines) with 1 INR-based example.\n"
    base += "- Keep answer and example on separate lines.\n"
    return base

# ------------------ Detect Language ------------------
def detect_user_language(text):
    try:
        return detect(text.strip())
    except:
        return "en"

# ------------------ GPT Function ------------------
def get_bank_response(query, detail_level):
    lang = detect_user_language(query)
    prompt = build_prompt(detail_level)
    prompt += f"\nAnswer in: {lang.upper()}\n\nQuery: {query}"
    try:
        result = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.3,
        )
        return result.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"❌ GPT Error: {e}")
        return None

# ------------------ Form: Input + Buttons ------------------
with st.form("bank_genie_form"):
    detail_level = st.selectbox("Choose answer detail level:", ["Short", "Detailed"], key="detail_select")
    user_query = st.text_area("Ask your question (in any language):", key="query_input", height=100)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        submit = st.form_submit_button("Ask to Bank Genie")
    with col2:
        reset = st.form_submit_button("Clear")

# ------------------ Form Actions ------------------
if submit and user_query.strip():
    with st.spinner("Thinking like a banker..."):
        st.session_state.response = get_bank_response(user_query, detail_level)

if reset:
    clear_all()

# ------------------ Output ------------------
if st.session_state.response:
    reply = st.session_state.response
    if "\n\n" in reply:
        ans, ex = reply.split("\n\n", 1)
        st.markdown(f"**Answer:**\n{ans.strip()}")
        st.markdown(f"💡 *Example:* {ex.strip()}")
    else:
        st.markdown(f"**Answer:**\n{reply}")

# ------------------ Footer ------------------
st.markdown("""
---
<div style="text-align:center">
<small>🔐 Internal use only | © SuperAI Labs</small>
</div>
""", unsafe_allow_html=True)
