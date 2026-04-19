from dataclasses import dataclass, field
import time
from typing import Literal


@dataclass
class Message:
    role: Literal["user", "assistant"]
    content: str
    timestamp: float = field(default_factory=time.time)
    is_code: bool = False
    code_expanded: bool = False
    status: Literal["done", "thinking", "error"] = "done"
    image_path: str = ""
    mentions: list = field(default_factory=list)


messages: list[Message] = []
is_thinking: bool = False
active_model: str = "gemma4:4b"


def add_message(role, content, is_code=False, status="done", image_path="", mentions=None) -> Message:
    message = Message(
        role=role,
        content=content,
        is_code=is_code,
        status=status,
        image_path=image_path,
        mentions=mentions or [],
    )
    messages.append(message)
    return message


def clear_messages():
    global is_thinking
    messages.clear()
    is_thinking = False


def get_messages() -> list[Message]:
    return messages


def set_thinking(thinking: bool):
    global is_thinking
    is_thinking = thinking
