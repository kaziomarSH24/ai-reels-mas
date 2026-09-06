from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai_service import ai_agent
from app.core.response import ApiResponse

router = APIRouter()

class DialogueRequest(BaseModel):
    text: str

@router.post("/analyze")
def analyze_text(request: DialogueRequest):
    """
    Handles the POST request for text analysis.
    Validates input and delegates logic to AIService.
    """
    if not request.text or len(request.text.strip()) == 0:
        return ApiResponse.response_error(message="Text cannot be empty", status_code=400)
        
    try:
        result = ai_agent.analyze_dialogue(request.text)
        return ApiResponse.response_success(message="Analysis completed successfully", data=result)
    except Exception as e:
        return ApiResponse.response_error(message="Failed to analyze text", errors=str(e), status_code=500)
