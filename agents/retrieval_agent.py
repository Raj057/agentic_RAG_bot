import os
import faiss
import numpy as np
from core.embeddings import embed_query, load_chunks
from core.mcp import MCPMessage
from core.message_bus import MessageBus

VECTOR_PATH = "vector.index"
CHUNK_PATH = "chunks.npy"

class RetrievalAgent:
    def __init__(self, bus: MessageBus):
        self.agent_name = "RetrievalAgent"
        self.bus = bus
        self.bus.register_agent(self.agent_name)

        self.index = None
        self.chunks = None

    def run(self):
        while True:
            msg = self.bus.receive(self.agent_name)
            if msg.type == "USER_QUERY":
                query = msg.payload["query"]
                trace_id = msg.trace_id

                # Load index only when needed
                if self.index is None or self.chunks is None:
                    if not os.path.exists(VECTOR_PATH):
                        raise FileNotFoundError("No documents embedded yet. Please upload and ingest documents first.")
                    self.index = faiss.read_index(VECTOR_PATH)
                    self.chunks = load_chunks()

                q_embedding = embed_query(query)
                D, I = self.index.search(np.array([q_embedding]), k=5)
                raw_chunks = [self.chunks[i] for i in I[0]]
                seen = set()
                top_chunks = []
                for chunk in raw_chunks:
                    if chunk not in seen:
                        seen.add(chunk)
                        top_chunks.append(chunk)

                response = MCPMessage(
                    sender=self.agent_name,
                    receiver="LLMResponseAgent",
                    type_="CONTEXT_RESPONSE",
                    trace_id=trace_id,
                    payload={
                        "query": query,
                        "top_chunks": top_chunks
                    }
                )
                self.bus.send(response)
