"""Streamlit chat frontend for the RAG API."""

import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Rupak RAG Chat Bot",
    page_icon="🤖",
    layout="centered",
)

st.markdown("""
<style>
    .stApp { background-color: #f0f4f9; }
    .block-container { max-width: 760px; padding-top: 2rem; }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 🤖 Rupak RAG Chat Bot")
st.caption("Ask me anything about your uploaded documents. I will answer with citations.")
st.divider()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "text": "Hi there! 👋 I'm Rupak's RAG assistant. Ask me anything about your uploaded documents!",
            "citations": [],
        }
    ]

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "🧑"):
        st.write(msg["text"])
        if msg.get("citations"):
            with st.expander("📄 Sources", expanded=True):
                for i, c in enumerate(msg["citations"], 1):
                    source = c.get("source", "unknown")
                    page = c.get("page", "?")
                    quote = c.get("quote", "")
                    st.markdown(f"**[{i}] {source} — Page {page}**")
                    if quote:
                        st.caption(f'"{quote[:200]}"')

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Enter your message...")

if user_input and user_input.strip():
    # Show user message immediately
    st.session_state.messages.append({"role": "user", "text": user_input, "citations": []})
    with st.chat_message("user", avatar="🧑"):
        st.write(user_input)

    # Call API and show response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                resp = requests.post(
                    f"{API_URL}/query",
                    json={"question": user_input},
                    timeout=120,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data["answer"]
                    citations = data.get("citations", [])
                else:
                    answer = f"API error {resp.status_code}: {resp.text}"
                    citations = []
            except requests.exceptions.ConnectionError:
                answer = "Could not connect to the API. Make sure `uvicorn api:app --reload` is running on port 8000."
                citations = []

        st.write(answer)
        if citations:
            with st.expander("📄 Sources", expanded=True):
                for i, c in enumerate(citations, 1):
                    source = c.get("source", "unknown")
                    page = c.get("page", "?")
                    quote = c.get("quote", "")
                    st.markdown(f"**[{i}] {source} — Page {page}**")
                    if quote:
                        st.caption(f'"{quote[:200]}"')

    st.session_state.messages.append({"role": "assistant", "text": answer, "citations": citations})

# ── PDF Upload (sidebar) ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Knowledge Base")
    st.caption("Upload PDFs to add to the RAG knowledge base.")
    uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])
    if uploaded_file:
        if st.button("Ingest PDF", use_container_width=True):
            with st.spinner("Ingesting..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/ingest",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                        timeout=120,
                    )
                    if resp.status_code == 200:
                        st.success(resp.json()["message"])
                    else:
                        st.error(f"Error: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the API.")

    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "text": "Hi there! 👋 I'm Rupak's RAG assistant. Ask me anything about your uploaded documents!",
                "citations": [],
            }
        ]
        st.rerun()
