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

class GenerateReelRequest(BaseModel):
    source_url: str
    start_time: str
    duration: int
    output_filename: str

@router.post("/generate_reel")
def generate_reel(request: GenerateReelRequest):
    from app.services.video_service import VideoService
    import time
    
    video_service = VideoService()
    try:
        # Measure time taken
        start_time_proc = time.time()
        
        output_path = video_service.extract_and_crop_clip(
            source_url=request.source_url,
            start_time=request.start_time,
            duration=request.duration,
            output_filename=request.output_filename
        )
        
        elapsed_time = round(time.time() - start_time_proc, 2)
        
        return ApiResponse.response_success(
            message=f"Reel generated successfully in {elapsed_time}s", 
            data={"output_path": output_path, "filename": request.output_filename}
        )
    except Exception as e:
        return ApiResponse.response_error(message="Failed to generate reel", errors=str(e), status_code=500)
