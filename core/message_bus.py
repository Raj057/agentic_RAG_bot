from queue import Queue
from typing import Dict
from core.mcp import MCPMessage

class MessageBus:
    def __init__(self):
        self.queues: Dict[str, Queue] = {}

    def register_agent(self, agent_name: str):
        self.queues[agent_name] = Queue()

    def send(self, message: MCPMessage):
        if message.receiver not in self.queues:
            raise Exception(f"Agent '{message.receiver}' not registered.")
        self.queues[message.receiver].put(message)

    def receive(self, agent_name: str) -> MCPMessage:
        if agent_name not in self.queues:
            raise Exception(f"Agent '{agent_name}' not registered.")
        msg_dict = self.queues[agent_name].get()
        return msg_dict
