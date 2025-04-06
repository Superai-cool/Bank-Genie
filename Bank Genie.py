import streamlit as st
import openai
import os
import random

# ------------------ OpenAI Key ------------------
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# ------------------ App Config ------------------
st.set_page_config(page_title="💬 EasyReply", layout="centered")

# ------------------ Open Graph Preview ------------------
st.markdown("""
    <head>
        <meta property="og:title" content="EasyReply - Your AI Assistant for Google Reviews" />
        <meta property="og:description" content="Generate quick, professional responses to Google Reviews effortlessly with EasyReply." />
        <meta property="og:image" content="https://raw.githubusercontent.com/Superai-cool/Supercomment/17ed2f28487e60c4f2155a3d81e9ad5e89c107d5/Easyreply.png" />
    </head>
""", unsafe_allow_html=True)

# ------------------ Global Styling ------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif !important;
        }
        body {
            background-color: #f9fafb;
        }
        .block-container {
            max-width: 700px;
            margin: auto;
            padding-top: 2rem;
        }
        h1 {
            text-align: center;
            color: #111827;
            font-size: 2.5rem;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            text-align: center;
            color: #4b5563;
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 1.5rem;
        }
        label, .stTextArea label, .stSelectbox label {
            font-size: 1rem !important;
            font-weight: 500;
        }
        .stTextArea textarea,
        .stSelectbox div,
        .stButton button,
        .stMarkdown,
        .stAlert,
        .stTextInput input {
            font-family: 'Poppins', sans-serif !important;
            font-size: 1rem !important;
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
            background-color: #1d4ed8;
        }
        .regen-btn {
            background-color: #0ea5e9;
        }
        .clear-btn {
            background-color: #ef4444;
        }
        @media (max-width: 500px) {
            .btn-row {
                flex-direction: column;
            }
            .btn-row button {
                margin-bottom: 0.5rem;
            }
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ Prompt Builder ------------------
def build_prompt(review, tone):
    return f"""
You are a specialized GPT assistant designed solely for generating short, professional replies to Google Reviews.

ONLY respond with a reply (no explanations). Use the tone: {tone}.

REVIEW:
\"\"\"{review}\"\"\"

Rules:
- Only generate a short reply (20–50 words).
- No emojis.
- Don't use generic intros like "Dear Customer" unless it fits.
- Reflect tone and content of review.
- Stay authentic and specific.
- If review is not relevant, reply:
  "This GPT is designed only to generate short replies to Google Reviews. Please paste a review and select a tone to receive a reply."
"""

# ------------------ Generate Reply ------------------
def generate_reply():
    prompt = build_prompt(st.session_state.review, st.session_state.tone)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=random.uniform(0.6, 0.8),
            max_tokens=150
        )
        st.session_state.reply = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Error: {e}")
        st.session_state.reply = ""

# ------------------ Clear App Like Fresh ------------------
def clear_app():
    st.session_state.review = ""
    st.session_state.tone = "Professional"
    st.session_state.reply = ""
    st.rerun()

# ------------------ Session State Defaults ------------------
if "review" not in st.session_state:
    st.session_state.review = ""
if "tone" not in st.session_state:
    st.session_state.tone = "Professional"
if "reply" not in st.session_state:
    st.session_state.reply = ""

# ------------------ Title + Intro ------------------
st.markdown("<h1>💬 EasyReply</h1>", unsafe_allow_html=True)
st.markdown("""
<div class='subtitle'>
EasyReply uses AI to craft thoughtful, personalized responses to Google reviews.<br>
Turn every review into a relationship — easily and professionally.
</div>
""", unsafe_allow_html=True)

# ------------------ Review Input ------------------
st.session_state.review = st.text_area("📝 Paste Google Review", value=st.session_state.review, height=140)

# ------------------ Tone Selector ------------------
st.session_state.tone = st.selectbox(
    "🎯 Choose Reply Tone",
    ["Professional", "Friendly", "Empathetic", "Apologetic", "Appreciative"],
    index=["Professional", "Friendly", "Empathetic", "Apologetic", "Appreciative"].index(st.session_state.tone)
)

# ------------------ Buttons ------------------
st.markdown('<div class="btn-row">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("✨ Generate Reply", type="primary"):
        if st.session_state.review.strip():
            generate_reply()
        else:
            st.warning("Please paste a review.")
with col2:
    if st.button("🔄 Regenerate"):
        if st.session_state.reply:
            generate_reply()
        else:
            st.warning("Generate a reply first.")
with col3:
    if st.button("🧹 Clear"):
        clear_app()
st.markdown('</div>', unsafe_allow_html=True)

# ------------------ Output ------------------
if st.session_state.reply:
    st.markdown("### ✅ Suggested Reply")
    st.markdown(f"<div class='response-box'>{st.session_state.reply}</div>", unsafe_allow_html=True)

# ------------------ Footer ------------------
st.markdown("""
<hr style='margin-top: 3rem; margin-bottom: 1rem;'>
<div style='text-align: center; font-size: 0.9rem; color: #6b7280; font-family: "Poppins", sans-serif;'>
✨ Made with ❤️ Developed by <strong>SuperAI Labs</strong> 🤖
</div>
""", unsafe_allow_html=True)
