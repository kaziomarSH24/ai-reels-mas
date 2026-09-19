from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from app.core.response import ApiResponse
from app.services.gemini_service import GeminiService
from app.services.whisper_service import WhisperService
from app.services.subtitle_service import SubtitleService
from app.services.video_service import VideoService

load_dotenv('/var/www/.env')
router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
gemini_svc = GeminiService(api_key=GEMINI_API_KEY)
whisper_svc = WhisperService()

class AnalyzeVideoRequest(BaseModel):
    youtube_url: str

@router.post("/analyze_video")
def analyze_video(request: AnalyzeVideoRequest):
    try:
        sub_service = SubtitleService()
        dialogues = sub_service.fetch_and_parse(request.youtube_url)
        vtt_content = "\n".join([f"{d['start_time']} --> {d['end_time']}\n{d['text']}" for d in dialogues])
        
        extracted_vocabulary = gemini_svc.extract_all_vocabulary(vtt_content)
        
        accepted = []
        for item in extracted_vocabulary:
            # DO NOT use newline. Separate with a space so Laravel UI renders it nicely without cutting off!
            target_word_combined = f"{item.get('expression', '')} {item.get('dictionary_meaning', '')}"
            
            vocab_type = item.get("type", "ADVANCED_WORD")
            
            accepted.append({
                "start_time": str(item.get("rough_start", 0)),
                "end_time": str(item.get("rough_end", 0)),
                "text": item.get("original_sentence", ""),
                "analysis": {
                    "emotion": "Neutral", 
                    "emotion_confidence": 99.9, 
                    "cefr_level": vocab_type,   
                    "cefr_confidence": 99.9,    
                    "target_word": target_word_combined,
                    "translation": item.get("sentence_translation", "")
                }
            })
            
        stats = {
            "total_scanned": len(dialogues),
            "accepted_count": len(accepted),
            "rejected_count": 0 
        }
        
        return ApiResponse.response_success(
            message=f"Processed video. Found {len(accepted)} advanced expressions.", 
            data={"stats": stats, "accepted": accepted, "rejected": []}
        )
    except Exception as e:
        return ApiResponse.response_error(message="Failed to process video", errors=str(e), status_code=500)

class GenerateCompilationRequest(BaseModel):
    clips: List[Dict[str, Any]]
    output_filename: str

@router.post("/generate_compilation")
def generate_compilation(request: GenerateCompilationRequest):
    import time
    video_service = VideoService()
    try:
        start_time_proc = time.time()
        
        output_path = video_service.generate_compilation_reel(
            clips=request.clips,
            output_filename=request.output_filename
        )
        
        elapsed_time = round(time.time() - start_time_proc, 2)
        
        return ApiResponse.response_success(
            message=f"Reel generated successfully in {elapsed_time}s", 
            data={"output_path": output_path, "filename": request.output_filename}
        )
    except Exception as e:
        return ApiResponse.response_error(message="Failed to generate reel", errors=str(e), status_code=500)
