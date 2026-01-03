import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Block:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    blocker_id: uuid.UUID = field(default_factory=uuid.uuid4)
    blocked_id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.now)
