import streamlit as st
import openai
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

# --- Load OpenAI Key Securely ---
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

# --- Clear Handler ---
if clear:
    st.session_state.query_input = ""
    st.experimental_rerun()

# --- Load FAISS Vector DB ---
@st.cache_resource
def load_kb_index():
    return FAISS.load_local("bank_kb_index", OpenAIEmbeddings(), allow_dangerous_deserialization=True)

db = load_kb_index()

# --- Retrieve Context from KB ---
def get_context_from_kb(query):
    results = db.similarity_search(query, k=3)
    return "\n\n".join([doc.page_content for doc in results]) if results else ""

# --- Split Answer & Example ---
example_keywords = ["Example:", "उदाहरण:", "📌 Example:"]

def split_answer_example(text):
    for keyword in example_keywords:
        if keyword in text:
            parts = text.split(keyword, 1)
            return parts[0].strip(), keyword + parts[1].strip()
    return text.strip(), None

# --- Process Submission ---
if submit and st.session_state.query_input.strip():
    query = st.session_state.query_input.strip()
    format_type = st.session_state.format_selector
    kb_context = get_context_from_kb(query)

    if not kb_context:
        st.markdown("### ❌ Answer")
        st.error("Sorry, I couldn't find relevant information in the knowledge base.")
    else:
        system_prompt = f"""
You are Bank Genie, an assistant for Indian bank employees.

ONLY answer using the knowledge base content provided below.
Do not use external knowledge or guess.

---
KNOWLEDGE BASE:
\"\"\"
{kb_context}
\"\"\"
---

Instructions:
- Provide only factual responses found in the KB.
- Use the format: ✅ Answer + 📌 Example (only if found).
- If not found in KB, say: "Sorry, I couldn’t find relevant information in the knowledge base."
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
            result = response["choices"][0]["message"]["content"]
            answer, example = split_answer_example(result)

            st.markdown("### ✅ Answer")
            st.success(answer)
            if example:
                st.markdown("### 📌 Example")
                st.info(example)

        except openai.error.AuthenticationError:
            st.error("🚫 Authentication Error: Please check your OpenAI API key in Streamlit secrets.")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

# --- Footer ---
st.markdown("---")
st.markdown("Built with ❤️ by **SuperAI Labs** — Tailored for Indian Banks 🇮🇳")
