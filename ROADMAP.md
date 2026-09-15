# AI Reels Generator - Project Roadmap & Architecture 🚀

## 🏗️ Core Architecture: "Zero-Storage Smart Partial Download"
To solve the issue of server storage filling up with 100+ downloaded movies, we are implementing a highly efficient, storage-free architecture:
1. **Video Ingestion:** System takes a YouTube link, downloads the video temporarily.
2. **AI Transcription:** `faster-whisper` extracts all dialogues and exact timestamps.
3. **Database Saving:** The dialogues, timestamps, and YouTube video ID are saved in the Laravel database.
4. **Auto-Cleanup:** The downloaded large video is **instantly deleted**. (Storage cost = 0 GB).
5. **On-Demand Reel Generation:** When the user searches for a word (e.g., "Absolutely"), the system finds the timestamp in the DB, and uses `yt-dlp --download-sections` to fetch **only** that specific 3-5 second clip directly from YouTube. 

## 🎨 UI/UX Guidelines (React + Tailwind)
- **Design Language:** Premium SaaS look (inspired by Vercel, Linear, Stripe).
- **Aesthetic:** Clean, minimalist, and modern.
- **Rule:** Absolutely NO generic "AI-generated" feelings (avoid cliché glowing borders, excessive robot emojis, etc.).
- **Typography:** Professional fonts (Inter/Poppins) with clean glassmorphism and subtle transitions.

---

## 🗓️ The 4-Day Execution Plan (Post-Exam)

### Day 1: Ingestion Pipeline (Whisper AI & Database)
- [ ] Create UI tab: "Add Video to Library" (Paste YouTube URL).
- [ ] Set up `faster-whisper` in Python microservice.
- [ ] Pipeline: Download video -> Extract Audio -> Whisper Transcription -> Save to Laravel DB -> Delete Video.

### Day 2: The Smart Search & Fetch Engine
- [ ] Build the "Search by Emotion/Word" functionality in Laravel.
- [ ] Implement `yt-dlp` partial download logic in Python to fetch only the needed 5-second clips based on DB timestamps.
- [ ] Stitch multiple short clips together using `moviepy`.

### Day 3: Auto Subtitling Engine
- [ ] Translate the extracted English dialogue segments to Bangla.
- [ ] Use `moviepy` to automatically burn/render the translated text onto the stitched 9:16 vertical video.

### Day 4: Premium Dashboard & Automation Finalization
- [ ] Build the minimalist SaaS-grade React dashboard.
- [ ] Finalize the end-to-end automation (Click Generate -> View Reel -> Download).
- [ ] (Optional) Add Profanity/Toxic filter to reject bad words.
- [ ] (Optional) Add Redis caching for repeated searches.

### Day 5 (Bonus): Mass Auto-Ingestion Pipeline (Web Scraping)
- [ ] Build a Python Web Scraper (`BeautifulSoup` / `Playwright`).
- [ ] Scrape `cinefreak.net` to automatically find movie pages.
- [ ] Extract the `player.yagaverse.net` iframe links.
- [ ] Decode the URL to get the Direct `.mkv` and `.srt` links.
- [ ] Automatically parse the `.srt` and bulk-insert dialogues into the database!
- [ ] Result: A massive automated movie database built with zero manual effort!
