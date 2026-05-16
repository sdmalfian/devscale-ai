from fastapi import APIRouter

from app.schema import CompletionResponse, MessageInput
from app.services import generate_response

router = APIRouter()

@router.post("/completions", response_model=CompletionResponse)
def start_completion(body: MessageInput):
    response = generate_response(body.message)
    return CompletionResponse(response=response)