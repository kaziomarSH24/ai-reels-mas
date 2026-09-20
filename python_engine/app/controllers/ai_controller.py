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

        import time
        CHUNK_SIZE = 300
        extracted_vocabulary = []
        
        for i in range(0, len(dialogues), CHUNK_SIZE):
            chunk_dialogues = dialogues[i:i+CHUNK_SIZE]
            vtt_content = ""
            for j, d in enumerate(chunk_dialogues):
                actual_idx = i + j
                vtt_content += f"[ID: {actual_idx}] {d['text']}\n"
                
            chunk_vocab = gemini_svc.extract_all_vocabulary(vtt_content)
            extracted_vocabulary.extend(chunk_vocab)
            time.sleep(2)  # Prevent Gemini 429 rate limit inside the chunk loop
        
        # ID Mapping & Failsafe Logic
        processed_vocab = []
        for item in extracted_vocabulary:
            start_id = item.get("start_id")
            end_id = item.get("end_id")
            orig_sentence = item.get("original_sentence", "").lower()
            
            real_start = None
            real_end = None
            
            # Helper to check if text roughly matches the chunk text
            def text_matches(start_idx, end_idx, target_text):
                if start_idx < 0 or end_idx >= len(dialogues) or start_idx > end_idx:
                    return False
                combined = " ".join([dialogues[i]['text'] for i in range(start_idx, end_idx + 1)]).lower()
                # Check if at least some words match to verify ID correctness
                target_words = set(target_text.split())
                chunk_words = set(combined.split())
                overlap = target_words.intersection(chunk_words)
                return len(overlap) > max(1, len(target_words) // 3)

            # Check if IDs are valid and text actually matches
            if start_id is not None and end_id is not None and text_matches(start_id, end_id, orig_sentence):
                real_start = time_to_sec(dialogues[start_id].get('start_sec', dialogues[start_id]['start_time']))
                real_end = time_to_sec(dialogues[end_id].get('end_sec', dialogues[end_id]['end_time']))
            else:
                # Failsafe: Exact/Fuzzy Text Matching over the entire array
                best_start_id = -1
                best_end_id = -1
                max_overlap = 0
                target_words = set(orig_sentence.split())
                
                for i in range(len(dialogues)):
                    for j in range(i, min(i+5, len(dialogues))): # Check up to 5 chunks ahead
                        combined = " ".join([dialogues[k]['text'] for k in range(i, j+1)]).lower()
                        chunk_words = set(combined.split())
                        overlap = len(target_words.intersection(chunk_words))
                        
                        if overlap > max_overlap:
                            max_overlap = overlap
                            best_start_id = i
                            best_end_id = j
                            
                if best_start_id != -1 and max_overlap > max(1, len(target_words) // 3):
                    real_start = time_to_sec(dialogues[best_start_id].get('start_sec', dialogues[best_start_id]['start_time']))
                    real_end = time_to_sec(dialogues[best_end_id].get('end_sec', dialogues[best_end_id]['end_time']))

            if real_start is not None and real_end is not None:
                item['rough_start'] = real_start
                item['rough_end'] = real_end
                processed_vocab.append(item)
                
        extracted_vocabulary = processed_vocab
        
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

class TranslateWordRequest(BaseModel):
    word: str

@router.post("/translate_word")
def translate_word(request: TranslateWordRequest):
    """
    Fetches a fresh, highly contextual, and daily-usable translation and example 
    for a specific word/phrase using Gemini AI.
    """
    try:
        import json
        prompt = f"""
        Provide a highly practical, daily-use Bengali translation and easy example for the English expression: "{request.word}".
        Return ONLY valid JSON in the exact format:
        {{
            "casual_meaning": "Bengali meaning",
            "easy_example": "A very simple English daily-use example sentence using the phrase.",
            "example_translation": "Bengali translation of the easy example."
        }}
        """
        response = gemini_svc.model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        
        return ApiResponse.response_success(
            message="Translated successfully", 
            data=data
        )
    except Exception as e:
        return ApiResponse.response_error(message="Translation failed", errors=str(e), status_code=500)
