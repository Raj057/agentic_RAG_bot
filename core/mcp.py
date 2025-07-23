from typing import Dict, Any
import uuid

class MCPMessage:
    def __init__(self, sender: str, receiver: str, type_: str, payload: Dict[str, Any], trace_id: str = None):
        self.sender = sender
        self.receiver = receiver
        self.type = type_
        self.payload = payload
        self.trace_id = trace_id or str(uuid.uuid4())

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "type": self.type,
            "trace_id": self.trace_id,
            "payload": self.payload
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]):
        return MCPMessage(
            sender=d["sender"],
            receiver=d["receiver"],
            type_=d["type"],
            trace_id=d["trace_id"],
            payload=d["payload"]
        )
