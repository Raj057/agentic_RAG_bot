from core.mcp import MCPMessage
from core.message_bus import MessageBus
from core.groq_llm import call_groq_llm

class LLMResponseAgent:
    def __init__(self, bus: MessageBus):
        self.agent_name = "LLMResponseAgent"
        self.bus = bus
        self.bus.register_agent(self.agent_name)

    def run(self):
        while True:
            msg = self.bus.receive(self.agent_name)
            if msg.type == "CONTEXT_RESPONSE":
                query = msg.payload["query"]
                context_chunks = msg.payload["top_chunks"]
                trace_id = msg.trace_id

                # Construct prompt
                context = "\n---\n".join(context_chunks)
                prompt = f"""You are a helpful assistant. Use the context below to answer the user's question.

Context:
{context}

Question: {query}
Answer:"""

                # Call Groq LLM
                answer = call_groq_llm(prompt)

                response = MCPMessage(
                    sender=self.agent_name,
                    receiver="UI",  # or CoordinatorAgent if exists
                    type_="LLM_RESPONSE",
                    trace_id=trace_id,
                    payload={
                        "answer": answer,
                        "source_chunks": context_chunks
                    }
                )
                self.bus.send(response)
