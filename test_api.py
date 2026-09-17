import requests
import json

data = {
    "clips": [
        {
            "source_url": "https://www.youtube.com/watch?v=zu81HU32BhE",
            "start_time": "00:00:00.000",
            "duration": 7,
            "english_text": "You brought a 90-lb asthmatic onto my army base.",
            "bengali_text": "তুমি আমার সেনা ঘাঁটিতে একজন ৯০ পাউন্ডের হাঁপানি রোগীকে নিয়ে এসেছ।",
            "target_word": "asthmatic"
        }
    ],
    "output_filename": "test_api_asthmatic.mp4"
}

r = requests.post("http://localhost:8001/api/generate_compilation", json=data)
print(r.status_code)
print(r.text)
