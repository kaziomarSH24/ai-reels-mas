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

from typing import List

class BatchDialogueRequest(BaseModel):
    texts: List[str]

@router.post("/analyze_batch")
def analyze_batch(request: BatchDialogueRequest):
    if not request.texts:
        return ApiResponse.response_error(message="Text list cannot be empty", status_code=400)
        
    try:
        results = []
        for text in request.texts:
            if text.strip():
                # For thesis performance, we process one by one in the batch
                res = ai_agent.analyze_dialogue(text)
                results.append({"text": text, "analysis": res})
            else:
                results.append({"text": text, "analysis": None})
                
        return ApiResponse.response_success(message="Batch analysis completed", data={"results": results})
    except Exception as e:
        return ApiResponse.response_error(message="Failed to analyze batch", errors=str(e), status_code=500)

class AnalyzeVideoRequest(BaseModel):
    youtube_url: str

@router.post("/analyze_video")
def analyze_video(request: AnalyzeVideoRequest):
    from app.services.subtitle_service import SubtitleService
    
    try:
        sub_service = SubtitleService()
        dialogues = sub_service.fetch_and_parse(request.youtube_url)
        
        # We don't want to run heavy NLP on 1000 lines instantly (takes too long).
        # We will return the dialogues to Laravel, and Laravel can request analysis 
        # on specific lines or store them all.
        # Alternatively, we can just process a random sample or run CEFR to filter.
        # For performance, let's just return the extracted data.
        
        return ApiResponse.response_success(
            message=f"Extracted {len(dialogues)} dialogues", 
            data={"dialogues": dialogues}
        )
    except Exception as e:
        return ApiResponse.response_error(message="Failed to process video", errors=str(e), status_code=500)

class GenerateReelRequest(BaseModel):
    source_url: str
    start_time: str
    duration: int
    output_filename: str
    english_text: str
    bengali_text: str

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
            output_filename=request.output_filename,
            english_text=request.english_text,
            bengali_text=request.bengali_text
        )
        
        elapsed_time = round(time.time() - start_time_proc, 2)
        
        return ApiResponse.response_success(
            message=f"Reel generated successfully in {elapsed_time}s", 
            data={"output_path": output_path, "filename": request.output_filename}
        )
    except Exception as e:
        return ApiResponse.response_error(message="Failed to generate reel", errors=str(e), status_code=500)
