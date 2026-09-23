import time
import os
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ScraperService:
    def __init__(self):
        # We will initialize the browser inside the method to save memory when not scraping
        pass

    def get_browser(self):
        from pyvirtualdisplay import Display
        # Start a virtual display (Xvfb)
        self.display = Display(visible=0, size=(1920, 1080))
        self.display.start()
        
        options = uc.ChromeOptions()
        # Removed --headless to trick Cloudflare
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-extensions')
        options.add_argument('--mute-audio')
        
        # explicitly provide the paths for docker debian chromium
        driver = uc.Chrome(
            options=options,
            driver_executable_path='/usr/bin/chromedriver',
            browser_executable_path='/usr/bin/chromium'
        ) 
        return driver

    def scrape_clips_for_word(self, target_word: str, max_clips: int = 5):
        """
        Train the bot to go to PlayPhrase.me, search the word, 
        and extract direct MP4 links, completely bypassing Cloudflare Turnstile.
        """
        print(f"[Scraper Bot] Starting search for: {target_word} on PlayPhrase")
        driver = None
        
        try:
            driver = self.get_browser()
            url = f"https://www.playphrase.me/#/search?q={target_word.replace(' ', '+')}"
            driver.get(url)
            
            # Wait for the first video to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'video'))
            )
            
            time.sleep(2) # Give it a moment to initialize the playlist
            
            # Extract video URLs from the Javascript state or DOM
            # Playphrase keeps a list of videos in window.__PRELOADED_STATE__ or we can just grab from video tags
            # Let's extract the current video and click 'next' a few times to grab more
            downloaded_paths = []
            seen = set()
            attempts = 0
            
            while len(downloaded_paths) < max_clips and attempts < 15:
                attempts += 1
                try:
                    video = driver.find_element(By.CSS_SELECTOR, 'video')
                    src = video.get_attribute('src')
                    
                    if src and src not in seen:
                        seen.add(src)
                        
                        clip_id = src.split('/')[-1].replace('.mp4', '')
                        out_path = f"/var/www/public/scraped_pp_{clip_id}.mp4"
                        
                        resp = requests.get(src, headers={'User-Agent': 'Mozilla/5.0'}, stream=True, timeout=15)
                        if resp.status_code == 200:
                            with open(out_path, 'wb') as f:
                                for chunk in resp.iter_content(chunk_size=1024*1024):
                                    f.write(chunk)
                            downloaded_paths.append(out_path)
                            
                        # Force PlayPhrase to go to the next video by simulating video end
                        driver.execute_script("document.querySelector('video').dispatchEvent(new Event('ended'));")
                        time.sleep(2) # Wait for the new video to load
                    else:
                        # If same video, simulate end again
                        time.sleep(1)
                        driver.execute_script("document.querySelector('video').dispatchEvent(new Event('ended'));")
                        
                except Exception as ex:
                    print(f"Error grabbing clip: {ex}")
                    time.sleep(1)
                    
            return downloaded_paths
            
        except Exception as e:
            print(f"[Scraper Bot] Error: {str(e)}")
            return []
        finally:
            if driver:
                driver.quit()
            if hasattr(self, 'display') and self.display:
                self.display.stop()
