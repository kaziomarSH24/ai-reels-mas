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
    from app.services.ai_service import ai_agent
    
    try:
        sub_service = SubtitleService()
        dialogues = sub_service.fetch_and_parse(request.youtube_url)
        
        accepted = []
        rejected = []
        
        # Analyze each line, filter for B2/C1
        # For a full movie this takes time, but for short clips (3-4 mins) it's fine.
        for item in dialogues:
            text = item['text']
            
            # Use CEFR model
            cefr_res = ai_agent.cefr_classifier(text)[0]
            level = cefr_res['label'].upper()
            confidence = round(cefr_res['score'] * 100, 2)
            
            if level in ['B2', 'C1', 'C2']:
                # Accepted - run full analysis (emotion, translation)
                full_analysis = ai_agent.analyze_dialogue(text)
                # Ensure confidence is included
                full_analysis['cefr_confidence'] = confidence
                
                accepted.append({
                    "start_time": item['start_time'],
                    "end_time": item['end_time'],
                    "text": text,
                    "analysis": full_analysis
                })
            else:
                # Rejected
                if len(rejected) < 20: # Keep sample of 20
                    rejected.append({
                        "text": text,
                        "reason": f"Level {level} is too easy (Confidence: {confidence}%)"
                    })
                    
        stats = {
            "total_scanned": len(dialogues),
            "accepted_count": len(accepted),
            "rejected_count": len(dialogues) - len(accepted)
        }
        
        return ApiResponse.response_success(
            message=f"Processed video. Found {len(accepted)} advanced dialogues.", 
            data={"stats": stats, "accepted": accepted, "rejected_sample": rejected}
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
