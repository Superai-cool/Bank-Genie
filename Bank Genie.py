# 🔧 Styling — Fix Top Spacing & Cleanup Layout
st.markdown("""
    <style>
    /* Reset top margin/padding from Streamlit's default */
    .main, .block-container {
        padding-top: 1rem !important;
    }

    /* Maintain clean layout and fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #f4f4f5;
    }

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
        text-align: center;
        font-size: 1rem;
        color: #52525b;
        margin-bottom: 1.5rem;
    }

    .response-box {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        padding: 1rem;
        margin-top: 1.5rem;
        border-radius: 8px;
        font-size: 1rem;
        line-height: 1.6;
        white-space: pre-wrap;
    }

    .button-row {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
    }

    .stButton > button {
        font-size: 1rem;
        padding: 0.65rem 1.2rem;
        border-radius: 6px;
        font-weight: 600;
        border: none;
    }

    .stButton > button:first-child {
        background-color: #2563eb;
        color: white;
    }

    .stButton > button:last-child {
        background-color: #ef4444;
        color: white;
    }

    @media (max-width: 600px) {
        .button-row {
            flex-direction: column;
        }
    }
    </style>
""", unsafe_allow_html=True)
