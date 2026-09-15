import urllib.request
import urllib.parse
import ssl
import re
import time
import json
import logging
import os
from bs4 import BeautifulSoup
import google.generativeai as genai
import mysql.connector

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Disable SSL verification for scraping
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# --- Gemini Setup ---
# The API key was saved in .env, in production we load it via python-dotenv. 
# For this script we will parse it manually or just use os.environ if it's there.
GEMINI_KEY = None
try:
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                GEMINI_KEY = line.strip().split("=")[1]
except Exception:
    pass

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    # Use standard pro/flash model
    model = genai.GenerativeModel('gemini-3.6-flash')
else:
    logging.warning("No GEMINI_API_KEY found in .env")

# --- MySQL Setup ---
def get_db_connection():
    return mysql.connector.connect(
        host="db", # Docker service name
        user="root",
        password="root",
        database="ai_reels_db"
    )

def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        return urllib.request.urlopen(req, context=ctx).read().decode("utf-8")
    except Exception as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return None

import base64

def extract_yagaverse_links(movie_url):
    html = fetch_html(movie_url)
    if not html: return None, None
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try to find generate.php links
    links = soup.find_all("a", href=re.compile(r'generate\.php\?id='))
    video_url = None
    subtitle_url = None # Cinefreak might not expose subtitles directly via generate.php
    
    for link in links:
        href = link['href']
        try:
            parsed = urllib.parse.urlparse(href)
            params = urllib.parse.parse_qs(parsed.query)
            encoded_id = params.get('id', [None])[0]
            if encoded_id:
                decoded_url = base64.b64decode(encoded_id).decode("utf-8")
                # Prefer 1080p or 720p if we can parse the text, but any is fine for now
                if "1080" in link.text or "720" in link.text or not video_url:
                    video_url = decoded_url
        except Exception as e:
            logging.error(f"Failed to decode link {href}: {e}")
            
    return video_url, subtitle_url

def scrape_movie_links(page_num):
    url = f"https://cinefreak.net/english-movies/page/{page_num}/"
    logging.info(f"Scraping {url}")
    html = fetch_html(url)
    if not html: return []

    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all("a", href=True)
    movies = {}
    
    for a in links:
        href = a["href"]
        text = a.text.strip()
        # cinefreak movie links usually have 4 slashes: https://cinefreak.net/movie-name/
        if "cinefreak.net" in href and href.count('/') == 4:
            if not any(x in href for x in ["/category/", "/page/", "/tag/", "/author/", "/about"]):
                if len(text) > 2: # Filter out empty links or icons
                    movies[href] = text
                    
    return [{"url": k, "title": v} for k, v in movies.items()]

def filter_movies_via_gemini(movies):
    if not GEMINI_KEY:
        return movies # Skip filter if no key
        
    titles = [m['title'] for m in movies]
    prompt = f"""
    Analyze these movie titles. Return ONLY a valid JSON array of objects.
    Each object must have "title" (exact match), "is_good" (boolean: true if it's a popular/high-quality English movie/series good for learning and reels, false if B-grade/obscure/adult), and "genre" (string).
    Titles:
    {json.dumps(titles)}
    """
    try:
        response = model.generate_content(prompt)
        # Strip markdown json block if exists
        text = response.text.replace('```json', '').replace('```', '').strip()
        result = json.loads(text)
        
        # Map results back
        filtered_movies = []
        for m in movies:
            for r in result:
                if r['title'] == m['title'] and r.get('is_good') == True:
                    m['genre'] = r.get('genre', '')
                    m['imdb_rating'] = 8.0 # Mock or ask AI for it
                    filtered_movies.append(m)
                    break
        return filtered_movies
    except Exception as e:
        logging.error(f"Gemini API Error: {e}")
        return []

def save_to_db(movie_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """INSERT IGNORE INTO movies 
                 (title, genre, imdb_rating, source_url, video_url, subtitle_url, is_processed, created_at, updated_at) 
                 VALUES (%s, %s, %s, %s, %s, %s, 0, NOW(), NOW())"""
        val = (
            movie_data['title'], 
            movie_data.get('genre'), 
            movie_data.get('imdb_rating', 0), 
            movie_data['url'], 
            movie_data.get('video_url'), 
            movie_data.get('subtitle_url')
        )
        cursor.execute(sql, val)
        conn.commit()
        logging.info(f"Saved to DB: {movie_data['title']}")
    except Exception as e:
        logging.error(f"DB Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def run_scraper():
    # Test just on page 1 for now
    movies = scrape_movie_links(1)
    logging.info(f"Found {len(movies)} raw movies on page 1.")
    
    # 2. Filter via Gemini API
    good_movies = filter_movies_via_gemini(movies)
    logging.info(f"Gemini approved {len(good_movies)} movies.")
    
    # 3. Extract direct links and save to DB
    for m in good_movies:
        v_url, s_url = extract_yagaverse_links(m['url'])
        if v_url:
            m['video_url'] = v_url
            m['subtitle_url'] = s_url
            save_to_db(m)
        else:
            logging.info(f"Skipping {m['title']} - No valid iframe found.")
        time.sleep(1) # Be polite to the server

if __name__ == "__main__":
    run_scraper()
