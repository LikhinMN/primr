from dataclasses import dataclass, field
from typing import Literal
import uuid


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    step: str = ""
    status: Literal[
        "pending",
        "generating",
        "ready",
        "executing",
        "done",
        "failed"
    ] = "pending"
    bpy_code: str = ""
    result: str = ""
    retry_count: int = 0
    depends_on: list = field(default_factory=list)
    error: str = ""
