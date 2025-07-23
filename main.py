# main.py

from agents.ingestion_agent import IngestionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.llm_response_agent import LLMResponseAgent
from core.message_bus import MessageBus
from core.mcp import MCPMessage
import threading
import time

bus = MessageBus()

# Init agents
ingest = IngestionAgent(bus)
retrieval = RetrievalAgent(bus)
llm = LLMResponseAgent(bus)

# Run agents
threading.Thread(target=ingest.run).start()
threading.Thread(target=retrieval.run).start()
threading.Thread(target=llm.run).start()

# Send doc for ingestion
bus.send(MCPMessage(
    sender="UI",
    receiver="IngestionAgent",
    type_="DOCUMENT_UPLOAD",
    payload={"files": ["docs/sample.pdf"]}
))

# Wait a few seconds (or automate wait-for-ready signals)
time.sleep(3)

# Send user query
bus.send(MCPMessage(
    sender="UI",
    receiver="RetrievalAgent",
    type_="USER_QUERY",
    payload={"query": "What KPIs were tracked in Q1?"}
))
