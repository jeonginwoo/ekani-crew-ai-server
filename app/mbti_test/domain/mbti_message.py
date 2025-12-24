from dataclasses import dataclass
from enum import Enum

class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"

class MessageSource(Enum):
    HUMAN = "human"
    AI = "ai"

@dataclass
class MBTIMessage:
    role: MessageRole
    content: str
    source: MessageSource