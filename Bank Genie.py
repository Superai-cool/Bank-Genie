import streamlit as st
import openai

# --- Set your OpenAI API key ---
openai.api_key = "your-api-key"

# --- Page Configuration ---
st.set_page_config(page_title="Bank Genie", layout="centered")

# --- App Title & Header ---
st.title("🏦 Bank Employees")
st.markdown("⚡ **Accurate** • 🧠 **Instant** • 💼 **Professional**")

# --- Input Area ---
st.text_input("❓ What’s your banking question?", key="query_input", label_visibility="collapsed")
answer_format = st.selectbox("📄 Choose Answer Format", ["Short", "Detailed"], key="format_selector")

# --- Buttons ---
col1, col2 = st.columns([1, 1])
with col1:
    submit = st.button("💬 Ask Bank Genie")
with col2:
    clear = st.button("🧹 Clear")

# --- Clear Functionality ---
if clear:
    st.session_state.query_input = ""
    st.experimental_rerun()

# --- Supported "Example" Keywords ---
example_keywords = ["Example:", "उदाहरण:", "उदाहरणार्थ:", "📌 Example:"]

# --- Answer/Example Splitter ---
def split_answer_example(response):
    for keyword in example_keywords:
        if keyword in response:
            parts = response.split(keyword, 1)
            answer = parts[0].strip()
            example = keyword + parts[1].strip()
            return answer, example
    return response.strip(), None

# --- Simulate Vector Search (Replace with real retrieval logic) ---
def get_context_from_kb(user_query):
    # 🔁 Replace this with actual PDF vector search (LangChain, FAISS, etc.)
    if "working capital" in user_query.lower():
        return """
Working capital finance is a short-term funding provided by banks to meet day-to-day operational expenses like salaries, rent, raw materials, etc. 
It is not used for long-term investments. Example: A retail business might apply for working capital finance to buy stock ahead of a holiday season.
"""
    return ""

# --- Ask Bank Genie ---
if submit and st.session_state.query_input.strip():
    query = st.session_state.query_input.strip()
    format_type = st.session_state.format_selector

    # Step 1: Retrieve relevant content
    kb_context = get_context_from_kb(query)

    if not kb_context:
        st.markdown("### ❌ Answer")
        st.error("Sorry, I couldn't find relevant information in the knowledge base.")
    else:
        # Step 2: Strict Prompt
        system_prompt = f"""
You are Bank Genie, an assistant for Indian bank employees.

ONLY use the following knowledge base content to answer the user's question. Do NOT use any outside knowledge or guess.

Knowledge Base:
\"\"\"
{kb_context}
\"\"\"

Respond in this format only:
✅ Answer: [short or detailed answer depending on user request]
📌 Example: [Only if found in the knowledge base]

If no answer or example is found in the knowledge base, clearly state that.
"""

        user_prompt = f"Question: {query}\nAnswer Format: {format_type}"

        # Step 3: Call OpenAI with strict context
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

        # Show Answer
        st.markdown("### ✅ Answer")
        st.success(answer)

        # Show Example
        if example:
            st.markdown("### 📌 Example")
            st.info(example)

# --- Footer ---
st.markdown("---")
st.markdown("Built with ❤️ by **SuperAI Labs** — Tailored for Indian Banks 🇮🇳")
