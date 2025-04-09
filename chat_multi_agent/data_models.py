from pydantic import BaseModel, Field


class Messages(BaseModel):
    role: str
    content: str


class ConversationBlocks(BaseModel):
    messages: list[Messages] = Field(default_factory=list)


class RequestPayLoad(BaseModel):
    model: str
    messages: list[dict[str, str]]
    stream: bool = True
    max_tokens: int
    temperature: float


class RequestContent(BaseModel):
    type: str
    text: str | None


class RequestDelta(BaseModel):
    text: str | None
    content: list[RequestContent] | None


class RequestStreamData(BaseModel):
    type: str
    delta: RequestDelta | None
    content: list[RequestContent] | None
