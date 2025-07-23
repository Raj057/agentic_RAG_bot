import os
from core.mcp import MCPMessage
from core.message_bus import MessageBus
from core.document_parser import parse_document
from core.embeddings import get_embeddings, save_embeddings

class IngestionAgent:
    def __init__(self, bus: MessageBus):
        self.agent_name = "IngestionAgent"
        self.bus = bus
        self.bus.register_agent(self.agent_name)

    def run(self):
        while True:
            msg = self.bus.receive(self.agent_name)
            if msg.type == "DOCUMENT_UPLOAD":
                file_paths = msg.payload["files"]
                trace_id = msg.trace_id

                all_chunks = []
                for path in file_paths:
                    chunks = parse_document(path)
                    all_chunks.extend(chunks)

                embeddings = get_embeddings(all_chunks)
                save_embeddings(embeddings, all_chunks)

                response = MCPMessage(
                    sender=self.agent_name,
                    receiver="RetrievalAgent",
                    type_="DOCUMENT_INGESTED",
                    trace_id=trace_id,
                    payload={"message": f"{len(all_chunks)} chunks embedded."}
                )
                self.bus.send(response)
