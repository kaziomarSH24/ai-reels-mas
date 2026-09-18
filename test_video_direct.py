import sys
sys.path.append('python_engine')
from app.services.video_service import VideoService

service = VideoService()
clips = [
    {
        "source_url": "https://www.youtube.com/watch?v=M2_NMqkEymY",
        "start_time": "00:03:13.720",
        "duration": 5,
        "english_text": "You brought a 90-lb asthmatic onto my army base.",
        "bengali_text": "hello",
        "target_word": "asthmatic"
    }
]

print("Starting video service...")
try:
    res = service.generate_compilation_reel(clips, "direct_test_reel.mp4")
    print("Success:", res)
except Exception as e:
    print("Error:", e)
