from pydantic import BaseModel, Field


class Messages(BaseModel):
    role: str
    content: str


class ConversationBlocks(BaseModel):
    messages: list[Messages] = Field(default_factory=list)


class RequestPayLoad(BaseModel):
    model: str
    messages: list[dict[str, str]]
    stream: bool
    max_tokens: int
    temperature: float


class RequestContent(BaseModel):
    type: str
    text: str | None = None


class RequestDelta(BaseModel):
    text: str | None = None
    content: list[RequestContent] | None = None


class RequestStreamData(BaseModel):
    type: str | None = None
    delta: RequestDelta | None = None
    content: list[RequestContent] | None = None
