import streamlit as st
import openai

# --- Page Configuration ---
st.set_page_config(page_title="Bank Genie", layout="centered")

# --- Title and Header ---
st.title("🏦 Internal Assistant for Indian Bank Employees")
st.markdown("⚡ **Accurate** • 🧠 **Instant** • 💼 **Professional**")

# --- Input UI ---
st.text_input("🔎 Ask a bank-related question", key="query_input", label_visibility="collapsed")
answer_format = st.selectbox("📝 Choose Answer Format", ["Short", "Detailed"], key="format_selector")

col1, col2 = st.columns([1, 1])
with col1:
    submit = st.button("💬 Ask Bank Genie")
with col2:
    clear = st.button("🧹 Clear")

# --- Clear functionality ---
if clear:
    st.session_state.query_input = ""
    st.experimental_rerun()

# --- Keyword mapping for multilingual "example" ---
example_keywords = ["Example:", "उदाहरण:", "उदाहरणार्थ:", "举例来说："]

# --- Split logic ---
def split_answer_example(response):
    for keyword in example_keywords:
        if keyword in response:
            parts = response.split(keyword, 1)
            answer = parts[0].strip()
            example = keyword + parts[1].strip()
            return answer, example
    return response.strip(), None

# --- Generate and show answer ---
if submit and st.session_state.query_input.strip() != "":
    query = st.session_state.query_input.strip()

    # 🔒 Replace below with your actual OpenAI call and system prompt
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Answer bank-related questions strictly from internal banking knowledge base. Format answer and example in one message using keywords like 'Example:' etc."},
            {"role": "user", "content": query}
        ],
        temperature=0.3
    )
    
    result = response['choices'][0]['message']['content']
    answer, example = split_answer_example(result)

    # ✅ Display Answer
    st.markdown("### ✅ Answer")
    st.success(answer)

    # 📌 Display Example if available
    if example:
        st.markdown("### 📌 Example")
        st.info(example)

# --- Footer ---
st.markdown("---")
st.markdown("Built with ❤️ by **SuperAI Labs** — Tailored for Indian Banks 🇮🇳")
