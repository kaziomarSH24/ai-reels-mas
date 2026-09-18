import requests

payload = {
    "clips": [
        {
            "source_url": "https://www.youtube.com/watch?v=M2_NMqkEymY",
            "start_time": "00:03:13.720",
            "duration": 5,
            "english_text": "You brought a 90-lb asthmatic onto my army base.",
            "bengali_text": "hello",
            "target_word": "asthmatic"
        }
    ],
    "output_filename": "test_reel.mp4"
}

print("Sending request...")
try:
    res = requests.post("http://localhost:8001/api/generate_compilation", json=payload, timeout=60)
    print(res.status_code)
    print(res.json())
except Exception as e:
    print("Error:", e)
