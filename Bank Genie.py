import streamlit as st
import openai
import os
from langdetect import detect
import uuid

# ------------------ Config ------------------
st.set_page_config(page_title="Bank Genie", layout="centered")

# ------------------ Load API ------------------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("API key missing.")
    st.stop()
openai.api_key = api_key

# ------------------ Session Setup ------------------
if "response" not in st.session_state:
    st.session_state.response = None
if "form_id" not in st.session_state:
    st.session_state.form_id = str(uuid.uuid4())  # Unique form ID

# ------------------ Reset Function ------------------
def reset_form():
    st.session_state.response = None
    st.session_state.form_id = str(uuid.uuid4())  # Force new form
    st.experimental_rerun()

# ------------------ Layout ------------------
st.title("🏦 Bank Genie - Internal Assistant")
st.markdown("Ask your banking question below. Genie will respond shortly.")

# ------------------ Form ------------------
with st.form(key=st.session_state.form_id):
    detail = st.selectbox("Choose answer detail level:", ["Short", "Detailed"])
    question = st.text_area("Ask your question:", height=100)

    col1, col2 = st.columns([3, 1])
    with col1:
        ask = st.form_submit_button("Ask to Bank Genie")
    with col2:
        clear = st.form_submit_button("Clear")

# ------------------ GPT Function ------------------
def get_response(q, d):
    lang = detect(q.strip()) if q.strip() else "en"
    prompt = (
        "You are Bank Genie, a multilingual internal assistant for bank staff.\n"
        "Only answer internal banking questions such as KYC, loans, deposits, etc.\n"
        "If irrelevant, reply: 'This assistant only answers internal bank-related queries.'\n"
        f"Provide a {'short' if d == 'Short' else 'detailed'} answer and 1 INR-based example.\n"
        "Answer and example should be clearly separated.\n"
        f"Language: {lang.upper()}\n\nQuestion: {q}"
    )
    try:
        res = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": q}
            ],
            temperature=0.3
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ GPT Error: {e}"

# ------------------ Logic ------------------
if ask and question.strip():
    with st.spinner("Thinking like a banker..."):
        st.session_state.response = get_response(question, detail)

if clear:
    reset_form()

# ------------------ Display ------------------
if st.session_state.response:
    r = st.session_state.response
    if "\n\n" in r:
        a, ex = r.split("\n\n", 1)
        st.markdown(f"**Answer:**\n{a.strip()}")
        st.markdown(f"💡 *Example:* {ex.strip()}")
    else:
        st.markdown(r)

# ------------------ Footer ------------------
st.markdown("---\n<center><small>🔐 Internal use only | Powered by SuperAI Labs</small></center>", unsafe_allow_html=True)
