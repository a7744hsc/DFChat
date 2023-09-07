from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import enum

class MessageStatus(enum.Enum):
    Ok = 0
    Pending = 1
    Error = 2


class ChatItem(BaseModel):
    sequence:int 
    sent_by_user: bool
    content: str
    status: MessageStatus

class DialogDTO(BaseModel):
    dialog_id: int|None
    chat_history: List[ChatItem]