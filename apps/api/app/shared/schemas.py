from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class CabinetAuthRequest(BaseModel):
    email: str
    full_name: str


class CabinetAuthResponse(BaseModel):
    user_id: int
    email: str
    full_name: str
    session_token: str
    expires_at: datetime


class ChatCreateRequest(BaseModel):
    title: str | None = None


class ChatResponse(BaseModel):
    id: int
    workspace_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    preview_first_message: str | None = None


class MessageCreateRequest(BaseModel):
    content: str


class UploadedFileResponse(BaseModel):
    id: int
    original_name: str
    mime_type: str
    size_bytes: int
    created_at: datetime
    download_path: str


class MessageResponse(BaseModel):
    id: int
    workspace_id: int
    chat_id: int
    role: str
    content: str
    status: str
    created_at: datetime
    updated_at: datetime
    attachments: list[UploadedFileResponse] = []


class AgentRunResponse(BaseModel):
    id: int
    workspace_id: int
    chat_id: int
    trigger_message_id: int
    output_message_id: int | None
    status: str
    error: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime


class MessagePostResponse(BaseModel):
    message_id: int
    agent_run_id: int
