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
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # explicitly provide the paths for docker debian chromium
        driver = uc.Chrome(
            options=options,
            driver_executable_path='/usr/bin/chromedriver',
            browser_executable_path='/usr/bin/chromium'
        ) 
        return driver

    def scrape_clips_for_word(self, target_word: str, max_clips: int = 5):
        """
        Train the bot to go to Yarn/PlayPhrase, search the word, 
        bypass Cloudflare, and extract direct MP4 links.
        """
        print(f"[Scraper Bot] Starting search for: {target_word}")
        driver = None
        
        try:
            driver = self.get_browser()
            url = f"https://getyarn.io/yarn-find?text={target_word.replace(' ', '+')}"
            driver.get(url)
            
            # Wait for Cloudflare challenge to pass and the grid to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href^="/yarn-clip/"]'))
            )
            
            # Extract URLs via JavaScript
            clip_hrefs = driver.execute_script(
                "return Array.from(document.querySelectorAll('a[href^=\"/yarn-clip/\"]')).map(a => a.href);"
            )
            
            # Deduplicate keeping order
            seen = set()
            unique_hrefs = [x for x in clip_hrefs if not (x in seen or seen.add(x))]
            
            downloaded_paths = []
            
            for href in unique_hrefs[:max_clips]:
                # Extract UUID: https://getyarn.io/yarn-clip/1234-abcd -> 1234-abcd
                clip_id = href.split('/')[-1]
                mp4_url = f"https://y.yarn.co/{clip_id}.mp4"
                
                # Download the MP4 directly
                out_path = f"/var/www/public/scraped_{clip_id}.mp4"
                
                # Using requests to download
                resp = requests.get(mp4_url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
                if resp.status_code == 200:
                    with open(out_path, 'wb') as f:
                        for chunk in resp.iter_content(chunk_size=1024*1024):
                            f.write(chunk)
                    downloaded_paths.append(out_path)
            
            return downloaded_paths
            
        except Exception as e:
            print(f"[Scraper Bot] Error: {str(e)}")
            return []
        finally:
            if driver:
                driver.quit()
