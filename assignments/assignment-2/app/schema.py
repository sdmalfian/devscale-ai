from pydantic import BaseModel

class MessageInput(BaseModel):
    message: str

class CompletionResponse(BaseModel):
    response: str
    