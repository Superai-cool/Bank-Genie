import streamlit as st
import openai
import os

# --- Secure API Key Loading ---
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Bank Genie", layout="centered")
st.title("🏦 Bank Employees")
st.markdown("⚡ **Accurate** • 🧠 **Instant** • 💼 **Professional**")

# --- User Inputs ---
st.text_input("❓ What’s your banking question?", key="query_input", label_visibility="collapsed")
answer_format = st.selectbox("📄 Choose Answer Format", ["Short", "Detailed"], key="format_selector")

col1, col2 = st.columns([1, 1])
with col1:
    submit = st.button("💬 Ask Bank Genie")
with col2:
    clear = st.button("🧹 Clear")

# --- Clear Functionality ---
if clear:
    st.session_state.query_input = ""
    st.experimental_rerun()

# --- Keywords for Example Splitting ---
example_keywords = ["Example:", "उदाहरण:", "उदाहरणार्थ:", "📌 Example:"]

def split_answer_example(response):
    for keyword in example_keywords:
        if keyword in response:
            parts = response.split(keyword, 1)
            answer = parts[0].strip()
            example = keyword + parts[1].strip()
            return answer, example
    return response.strip(), None

# --- Simulated Knowledge Base Context (replace with LangChain later) ---
def get_context_from_kb(user_query):
    if "working capital" in user_query.lower():
        return """
Working capital finance is a short-term funding provided by banks to meet day-to-day operational expenses like salaries, rent, raw materials, etc.
It is not used for long-term investments. Example: A retail business might apply for working capital finance to buy stock ahead of a holiday season.
"""
    return ""

# --- Answer Generation ---
if submit and st.session_state.query_input.strip():
    query = st.session_state.query_input.strip()
    format_type = st.session_state.format_selector

    # --- Get KB content ---
    kb_context = get_context_from_kb(query)

    if not kb_context:
        st.markdown("### ❌ Answer")
        st.error("Sorry, I couldn't find relevant information in the knowledge base.")
    else:
        system_prompt = f"""
You are Bank Genie, an assistant for Indian bank employees.

ONLY use the following knowledge base content to answer the user's question. Do NOT use any outside knowledge or guess.

Knowledge Base:
\"\"\"
{kb_context}
\"\"\"

Respond in this format only:
✅ Answer: [Short or Detailed based on user request]
📌 Example: [Only if found in knowledge base]

If no answer or example is present in the knowledge base, clearly state that.
"""

        user_prompt = f"Question: {query}\nAnswer Format: {format_type}"

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            result = response['choices'][0]['message']['content']
            answer, example = split_answer_example(result)

            st.markdown("### ✅ Answer")
            st.success(answer)

            if example:
                st.markdown("### 📌 Example")
                st.info(example)

        except openai.error.AuthenticationError:
            st.error("🚫 Authentication Error: Please check your OpenAI API key in Streamlit secrets.")
        except Exception as e:
            st.error(f"⚠️ Unexpected Error: {e}")

# --- Footer ---
st.markdown("---")
st.markdown("Built with ❤️ by **SuperAI Labs** — Tailored for Indian Banks 🇮🇳")
