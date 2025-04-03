import streamlit as st
import openai
import os
from PIL import Image
import base64
from io import BytesIO

# ------------------ App Configuration ------------------
st.set_page_config(
    page_title="Learn Kannada",
    page_icon="🗣️",
    layout="centered"
)

# ------------------ Styling ------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    section.main > div {
        padding-top: 1rem !important;
    }
    .stButton>button {
        background-color: #000000 !important;
        color: white !important;
        font-size: 16px;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
        border: none;
    }
    .stTextArea textarea {
        font-size: 16px;
        padding: 12px;
        border-radius: 10px;
    }
    .stTextArea {
        margin-bottom: -10px;
    }
    .centered-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 10px;
        padding: 0 5%;
    }
    .title {
        margin-top: 15px;
        font-size: 2.2rem;
        font-weight: 700;
    }
    .subtitle {
        font-size: 1.1rem;
        font-weight: 500;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .desc {
        font-size: 1rem;
        max-width: 600px;
        margin: 0 auto 20px;
    }
    .custom-label {
        text-align: center;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 10px;
        margin-top: -10px;
    }
    .markdown-text-container p {
        margin-bottom: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ Load OpenAI API Key ------------------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OpenAI API key not found. Please set it in your Streamlit Cloud Secrets or local environment.")
    st.stop()
openai.api_key = api_key

# ------------------ Embed Logo ------------------
def image_to_base64(img: Image.Image) -> str:
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

logo = Image.open("image.png")
encoded_logo = image_to_base64(logo)

# ------------------ App Header ------------------
st.markdown(
    f"""
    <div class="centered-container">
        <img src='data:image/png;base64,{encoded_logo}' width='100'>
        <div class="title">Learn Kannada</div>
        <div class="subtitle">Your Personal Coach for Easy Kannada Learning</div>
        <div class="desc">Ask anything in English (or your language) and get simple, step-by-step Kannada guidance to help you learn and speak with confidence.</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------ Updated Prompt without Hindi Transliteration ------------------
LEARN_KANNADA_PROMPT = """
You are "Learn Kannada" – a friendly assistant designed to help kids and beginners learn local, spoken Kannada step by step.

🟡 Always respond using this four-part format:

• **Kannada Translation:** Provide the modern, everyday Kannada word or sentence.

• **Transliteration (English):** Show pronunciation using English letters.

• **Meaning / Context:** Explain the meaning in very simple English.

• **Example Sentence:** Provide a short, real-life Kannada sentence. Include:
  - Kannada script  
  - English transliteration  
  - English translation

Speak like a local tutor teaching a child. Always use clear, friendly, beginner-level Kannada. Avoid overly formal or classical language.

If the user types something unrelated to Kannada learning, reply gently:
"Let’s keep learning Kannada together! Ask me anything you want to say in Kannada."
"""

# ------------------ GPT Call ------------------
def get_kannada_response(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": LEARN_KANNADA_PROMPT},
                {"role": "user", "content": query.strip()}
            ],
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()

        result = f"""
### ✅ Your Kannada Learning Result

{content}
"""
        return result

    except Exception as e:
        st.error(f"❌ OpenAI API Error:\n\n{e}")
        return ""

# ------------------ Input UI ------------------
st.markdown("<div class='custom-label'>💬 What would you like to learn in Kannada?</div>", unsafe_allow_html=True)

query = st.text_area(
    label="",
    placeholder="E.g., hello, thank you, I want water, milk, I'm hungry",
    height=140
)

# ------------------ Query Preprocessor ------------------
def preprocess_query(q):
    q = q.lower().strip()
    if not q:
        return ""
    if any(x in q for x in ["how", "say", "translate", "in kannada", "?"]):
        return q
    return f"How do I say '{q}' in Kannada?"

# ------------------ Button ------------------
if st.button("📝 Tell me in Kannada"):
    if query.strip():
        cleaned_query = preprocess_query(query)
        with st.spinner("Translating and formatting your answer..."):
            response = get_kannada_response(cleaned_query)
        if response:
            st.markdown(response)
    else:
        st.warning("⚠️ Please enter a valid question.")

# ------------------ Footer ------------------
st.markdown("""
---
<center><small>✨ Made with ❤️ to help you speak Kannada like a local!</small></center>
""", unsafe_allow_html=True)
