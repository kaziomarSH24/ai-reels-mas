from fastapi import FastAPI
from app.controllers.ai_controller import router as ai_router
from app.core.response import ApiResponse

app = FastAPI(title="AI Reels Microservice", description="FastAPI Backend for AI Video processing")

# Register Routes (Controllers)
app.include_router(ai_router, prefix="/api")

@app.get("/")
def root():
    """
    Health check endpoint for the Microservice.
    """
    return ApiResponse.response_success(message="AI Reels Microservice is running!")
