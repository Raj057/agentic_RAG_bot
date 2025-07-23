import streamlit as st
import sys
import os
import tempfile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.mcp import MCPMessage
from core.message_bus import MessageBus
import uuid


# Initialize shared MessageBus
from agents.ingestion_agent import IngestionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.llm_response_agent import LLMResponseAgent

# Startup
bus = MessageBus()  # ✅ REGISTER UI AS AN AGENT
import threading
from agents.ingestion_agent import IngestionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.llm_response_agent import LLMResponseAgent

def start_agents(bus):
    threading.Thread(target=IngestionAgent(bus).run, daemon=True).start()
    threading.Thread(target=RetrievalAgent(bus).run, daemon=True).start()
    threading.Thread(target=LLMResponseAgent(bus).run, daemon=True).start()

@st.cache_resource
def setup_bus_and_agents():
    bus = MessageBus()
    start_agents(bus)
    return bus

bus = setup_bus_and_agents()
bus.register_agent("UI")



st.set_page_config(page_title="📄 Agentic RAG Chatbot", layout="wide")
st.title("🤖 Agentic RAG Chatbot")
st.caption("Upload your documents & ask questions powered by MCP Agents")

# Session
if "trace_id" not in st.session_state:
    st.session_state["trace_id"] = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Upload UI
uploaded_files = st.file_uploader("📎 Upload your documents", type=["pdf", "docx", "pptx", "csv", "txt", "md"], accept_multiple_files=True)
if st.button("🔄 Ingest Documents") and uploaded_files:
    paths = []
    for file in uploaded_files:
        temp_path = os.path.join(tempfile.gettempdir(), file.name)
        with open(temp_path, "wb") as f:
            f.write(file.read())
        paths.append(temp_path)

    bus.send(MCPMessage(
        sender="UI",
        receiver="IngestionAgent",
        type_="DOCUMENT_UPLOAD",
        trace_id=st.session_state["trace_id"],
        payload={"files": paths}
    ))

    st.success("Documents sent for ingestion.")

# Chat UI
st.subheader("💬 Ask a Question")
query = st.text_input("Type your question here...")

if st.button("🚀 Get Answer") and query:
    bus.send(MCPMessage(
        sender="UI",
        receiver="RetrievalAgent",
        type_="USER_QUERY",
        trace_id=st.session_state["trace_id"],
        payload={"query": query}
    ))

    # Wait for answer from LLMResponseAgent
    with st.spinner("Thinking..."):
        msg = bus.receive("UI")
        if msg.type == "LLM_RESPONSE":
            answer = msg.payload["answer"]
            source = msg.payload["source_chunks"]

            st.session_state["chat_history"].append({"q": query, "a": answer, "context": source})

# Display chat
if st.session_state["chat_history"]:
    st.subheader("🧠 Chat History")
    for entry in reversed(st.session_state["chat_history"]):
        st.markdown(f"**User:** {entry['q']}")
        st.markdown(f"**AI:** {entry['a']}")
        with st.expander("📄 Source Context"):
            for chunk in entry["context"]:
                st.markdown(f"```\n{chunk.strip()}\n```")
