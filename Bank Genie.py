import streamlit as st
import openai
import os
from googletrans import Translator

# ------------------ App Configuration ------------------
st.set_page_config(page_title="Bank Genie - Internal Assistant", layout="centered")

# ------------------ Load OpenAI API Key ------------------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OpenAI API key not found. Please set it in your Streamlit Cloud Secrets or local environment.")
    st.stop()
openai.api_key = api_key

# ------------------ Styling ------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #f8f9fa;
    }
    section.main > div {
        padding-top: 1rem !important;
    }
    .block-container {
        max-width: 600px;
        background-color: white;
        border-radius: 1.5rem;
        padding: 2rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin: auto;
    }
    .stTextInput>div>div>input {
        border-radius: 0.75rem;
        padding: 1rem;
        font-size: 1rem;
    }
    .stButton>button {
        background-color: #000000;
        color: white;
        font-size: 16px;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ UI Title ------------------
st.title("🏦 Bank Genie - Internal Q&A Assistant")
st.markdown("""
Welcome to **Bank Genie**, your internal multilingual assistant. Ask any bank-related question below. 

🔹 Responses will be short, summarized, and include simple examples.  
🔒 Non-banking queries will be politely declined.
""")

# ------------------ Input ------------------
user_query = st.text_input("Ask your question (in any language):", max_chars=300)

# ------------------ Translator ------------------
translator = Translator()

# ------------------ GPT Prompt ------------------
BANK_GENIE_PROMPT = """
You are an internal assistant used only by bank employees. Answer only bank-related questions such as:
- Account operations (KYC, dormant, joint holders)
- Cash handling (deposit rules, limits)
- Loans, credit processing, and documentation
- NEFT, RTGS, UPI, IMPS, cheque handling
- Compliance, RBI rules, internal policies
- Core banking systems and internal tools
- HR-related internal queries only if tied to bank policies

🚫 Never answer unrelated topics (e.g., jokes, weather, news). Reply: "I’m designed to answer only internal bank-related questions. Please ask something related to banking."

✅ For valid queries:
1. Respond with a short, summarized answer (1-3 lines)
2. Include 1 simple example per answer
3. Answer in the **same language** as the question
"""

# ------------------ GPT Call ------------------
def get_bank_response(query):
    try:
        detected_lang = translator.detect(query).lang

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": BANK_GENIE_PROMPT},
                {"role": "user", "content": query.strip()}
            ],
            temperature=0.3
        )
        answer = response.choices[0].message.content.strip()
        translated_answer = translator.translate(answer, dest=detected_lang).text if detected_lang != 'en' else answer
        return translated_answer
    except Exception as e:
        st.error(f"❌ GPT Error: {e}")
        return None

# ------------------ Output ------------------
if user_query:
    with st.spinner("Thinking like a banker..."):
        reply = get_bank_response(user_query)
        if reply:
            st.markdown(f"### ✅ Answer\n{reply}")

# ------------------ Footer ------------------
st.markdown("""
---
<center><small>🔐 For internal banking use only | Powered by OpenAI & Streamlit</small></center>
""", unsafe_allow_html=True)
