from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

from app.core.response import ApiResponse
from app.services.gemini_service import GeminiService
from app.services.subtitle_service import SubtitleService
from app.services.video_service import VideoService

# Load environment variables
load_dotenv('/var/www/.env')
router = APIRouter()

# Initialize API Services
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
gemini_svc = GeminiService(api_key=GEMINI_API_KEY)

class AnalyzeVideoRequest(BaseModel):
    youtube_url: str

@router.post("/analyze_video")
def analyze_video(request: AnalyzeVideoRequest):
    """
    Phase 1: Downloads VTT subtitles and passes them to Gemini AI 
    to extract casual vocabulary, idioms, and daily phrases.
    """
    try:
        sub_service = SubtitleService()
        dialogues = sub_service.fetch_and_parse(request.youtube_url)
        def time_to_sec(t):
            if isinstance(t, (int, float)): return t
            if ':' not in str(t): return float(t)
            parts = str(t).split(':')
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])

        vtt_content = "\n".join([f"{time_to_sec(d.get('start_sec', d['start_time']))} --> {time_to_sec(d.get('end_sec', d['end_time']))}\n{d['text']}" for d in dialogues])
        
        extracted_vocabulary = gemini_svc.extract_all_vocabulary(vtt_content)
        
        # We pass the extracted vocabulary directly. The schema now perfectly
        # matches the updated Laravel VideoClip model expectations.
        stats = {
            "total_scanned": len(dialogues),
            "extracted_count": len(extracted_vocabulary)
        }
        
        return ApiResponse.response_success(
            message=f"Analyzed video. Extracted {len(extracted_vocabulary)} smart phrases.", 
            data={"stats": stats, "extracted_clips": extracted_vocabulary}
        )
    except Exception as e:
        return ApiResponse.response_error(message="Failed to analyze video", errors=str(e), status_code=500)


class GenerateCompilationRequest(BaseModel):
    clips: List[Dict[str, Any]]
    output_filename: str

@router.post("/generate_compilation")
def generate_compilation(request: GenerateCompilationRequest):
    """
    Phase 2: Compiles a viral reel using Whisper AI for precise micro-syncing 
    and FFmpeg for video rendering.
    """
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
