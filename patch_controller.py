with open("python_engine/app/controllers/ai_controller.py", "r") as f:
    content = f.read()

new_endpoint = """
from typing import List

class ClipItem(BaseModel):
    source_url: str
    start_time: str
    duration: int
    english_text: str
    bengali_text: str
    target_word: str

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
"""

content = content + "\n" + new_endpoint

with open("python_engine/app/controllers/ai_controller.py", "w") as f:
    f.write(content)

