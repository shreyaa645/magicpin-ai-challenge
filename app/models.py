from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class ContextRequest(BaseModel):
    scope: str
    context_id: str
    version: int
    payload: Dict[str, Any]
    delivered_at: str


class ContextResponse(BaseModel):
    accepted: bool


class TickRequest(BaseModel):
    now: str
    available_triggers: List[str]


class TickAction(BaseModel):
    trigger_id: str
    merchant_id: str
    body: str
    cta: str
    send_as: str


class TickResponse(BaseModel):
    actions: List[TickAction]


class ReplyRequest(BaseModel):
    conversation_id: str
    merchant_id: str
    customer_id: Optional[str] = None
    from_role: str
    message: str
    received_at: str
    turn_number: int


class ReplyResponse(BaseModel):
    action: str
    body: str
    wait_seconds: int


class MetadataResponse(BaseModel):
    team_name: str
    model: str
    version: str


class HealthResponse(BaseModel):
    status: str