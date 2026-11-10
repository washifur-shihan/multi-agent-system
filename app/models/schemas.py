from typing import Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    customer_key: str = Field(default="aurora-user", description="Unique client or call identifier")
    message: str = Field(default="", description="User query or voice transcript")
    channel: str = Field(default="chat", description="Channel: 'chat' or 'voice'")
    agent_slug: str = Field(default="master", description="Target agent slug or 'master' for auto-routing")
    auto_route: bool = Field(default=True, description="Allow cross-department routing if query matches another specialist")


class ChatResponse(BaseModel):
    reply: str
    agent: str
    agent_name: str
    route_reason: str
    transferred: bool = False
    knowledge_used: int = 0
    conversation_id: Optional[str] = None


class ResetChatRequest(BaseModel):
    customer_key: str = "aurora-user"
    channel: str = "chat"
    agent_slug: str = "master"


class KnowledgeSearchRequest(BaseModel):
    query: str
    agent_slug: str = "master"
    match_count: int = 5


class VapiEventRequest(BaseModel):
    type: Optional[str] = None
    message: Optional[Any] = None
