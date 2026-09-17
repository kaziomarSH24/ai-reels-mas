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
        valid_texts = [t for t in request.texts if t.strip()]
        
        batch_results = []
        if valid_texts:
            batch_results = ai_agent.batch_analyze_dialogues(valid_texts)
            
        results = []
        valid_idx = 0
        for text in request.texts:
            if text.strip():
                results.append({"text": text, "analysis": batch_results[valid_idx]})
                valid_idx += 1
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
        
        # Extract all texts
        texts = [item['text'] for item in dialogues]
        
        # Run BATCH analysis on all texts at once
        batch_results = ai_agent.batch_analyze_dialogues(texts)
        
        for i, item in enumerate(dialogues):
            full_analysis = batch_results[i]
            level = full_analysis['cefr_level']
            
            if level in ['IDIOM', 'HARD_WORD']:
                accepted.append({
                    "start_time": item['start_time'],
                    "end_time": item['end_time'],
                    "text": full_analysis.get('fixed_english', item['text']),
                    "analysis": full_analysis
                })
            else:
                rejected.append({
                    "start_time": item['start_time'],
                    "end_time": item['end_time'],
                    "text": full_analysis.get('fixed_english', item['text']),
                    "analysis": full_analysis
                })
                    
        stats = {
            "total_scanned": len(dialogues),
            "accepted_count": len(accepted),
            "rejected_count": len(rejected)
        }
        
        return ApiResponse.response_success(
            message=f"Processed video. Found {len(accepted)} advanced dialogues.", 
            data={"stats": stats, "accepted": accepted, "rejected": rejected}
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


from typing import List

class ClipItem(BaseModel):
    source_url: str
    start_time: str
    duration: int
    english_text: str
    bengali_text: str
    target_word: str
    dictionary_meaning: str | None = None

class GenerateCompilationRequest(BaseModel):
    clips: List[ClipItem]
    output_filename: str

@router.post("/generate_compilation")
def generate_compilation(request: GenerateCompilationRequest):
    from app.services.video_service import VideoService
    import time
    
    video_service = VideoService()
    try:
        start_time_proc = time.time()
        
        # Convert Pydantic models to dicts
        clip_dicts = [clip.dict() for clip in request.clips]
        
        output_path = video_service.generate_compilation_reel(
            clips=clip_dicts,
            output_filename=request.output_filename
        )
        
        elapsed_time = round(time.time() - start_time_proc, 2)
        
        return ApiResponse.response_success(
            message=f"Compilation Reel generated successfully in {elapsed_time}s", 
            data={"output_path": output_path, "filename": request.output_filename}
        )
    except Exception as e:
        return ApiResponse.response_error(message="Failed to generate compilation reel", errors=str(e), status_code=500)
