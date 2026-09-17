import webvtt

def timestamp_to_seconds(ts):
    # '00:00:15.539' -> seconds
    h, m, s = ts.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)

def parse_vtt(file_path):
    import webvtt
    import re
    captions = webvtt.read(file_path)
    
    transcript = []
    for caption in captions:
        text = caption.text.strip()
        # Clean up weird yt-dlp vtt tags like <c> or <00:00:01.000>
        text = re.sub(r'<[^>]+>', '', text)
        # yt-dlp auto-subs often have duplicate lines because of roll-up
        # But webvtt parses it. We just need to take unique text lines
        lines = text.split('\n')
        text = ' '.join(set(lines)).strip()
        
        transcript.append({
            'text': text,
            'start': timestamp_to_seconds(caption.start),
            'duration': timestamp_to_seconds(caption.end) - timestamp_to_seconds(caption.start)
        })
    return transcript
