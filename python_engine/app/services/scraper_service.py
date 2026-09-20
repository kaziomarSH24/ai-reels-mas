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
        
        # This is where the magic happens to bypass Cloudflare
        driver = uc.Chrome(options=options, version_main=115) 
        return driver

    def scrape_clips_for_word(self, target_word: str, max_clips: int = 5):
        """
        Train the bot to go to Yarn/PlayPhrase, search the word, 
        bypass Cloudflare, and extract direct MP4 links.
        """
        print(f"[Scraper Bot] Starting search for: {target_word}")
        driver = self.get_browser()
        
        try:
            # Step 1: Go to the website (e.g., Yarn)
            url = f"https://getyarn.io/yarn-find?text={target_word.replace(' ', '+')}"
            driver.get(url)
            
            # Step 2: Wait for Cloudflare to pass (The "Just a moment" screen)
            # We train the bot to wait until the real video elements appear on screen
            time.sleep(5) 
            
            # TODO: Add logic to extract the exact MP4 links from the DOM
            # clips = driver.find_elements(By.CSS_SELECTOR, '.clip-wrap video source')
            
            downloaded_paths = []
            
            # Step 3: Download them
            # for link in clip_links[:max_clips]:
            #     download_to_tmp()
                
            return downloaded_paths
            
        except Exception as e:
            print(f"[Scraper Bot] Error: {str(e)}")
            return []
        finally:
            driver.quit()
