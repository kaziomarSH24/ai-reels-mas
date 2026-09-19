# SnapClip AI - Data Extraction Schema (Phase 1)

This schema defines the structured JSON output expected from Gemini when parsing VTT subtitles.

## JSON Schema

```json
[
  {
    "expression": "I'm broke",
    "whisper_target": "I'm completely broke",
    "category": "DAILY_PHRASE",
    "casual_meaning": "পকেট ফাঁকা / টাকা-পয়সা না থাকা",
    "original_sentence": "I'd love to grab a coffee with you, but honestly, I'm completely broke right now.",
    "original_translation": "তোমার সাথে কফি খেতে ভালোই লাগতো, কিন্তু সত্যি বলতে, আমার পকেট এখন একদম ফাঁকা।",
    "easy_example": "I can't buy that shirt, I'm broke.",
    "example_translation": "আমি ওই শার্টটা কিনতে পারবো না, আমার কাছে টাকা নেই।",
    "rough_start": 40.50,
    "rough_end": 45.00
  }
]
```

## Field Definitions
- **`expression`**: The clean, base form of the word or idiom (for UI display & text overlay on the Reel).
- **`whisper_target`**: The EXACT verbatim phrase spoken in the video, including filler words. Used by Whisper AI in Phase 2 to ensure frame-perfect cropping.
- **`category`**: Enum classification (`IDIOM`, `ADVANCED_WORD`, `DAILY_PHRASE`).
- **`casual_meaning`**: Conversational, everyday Bengali meaning (not formal dictionary language).
- **`original_sentence`**: The full, complete merged sentence from the video subtitle.
- **`original_translation`**: Casual Bengali translation of the original sentence.
- **`easy_example`**: A generated short, simple 3-5 word sentence using the expression to help users learn.
- **`example_translation`**: Bengali translation of the easy example.
- **`rough_start`**: Approximate start timestamp of the sentence (in seconds).
- **`rough_end`**: Approximate end timestamp of the sentence (in seconds).
