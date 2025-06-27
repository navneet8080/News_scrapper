import logging
import os
import time
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

# === Logging Setup ===
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/aajtak_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AajTakScraper:
    def __init__(self):
        self.driver = self._setup_driver()
        self.news_data = []

    def _setup_driver(self):
        options = Options()
        chrome_args = [
            "--start-maximized",
            "--disable-infobars",
            "--disable-notifications",
            "--disable-extensions",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled"
        ]
        for arg in chrome_args:
            options.add_argument(arg)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(3)
        return driver

    def open_and_click(self):
        logger.info("Opening AajTak homepage and clicking target element...")
        self.driver.get("https://www.aajtak.in")
        try:
            xpath = "/html/body/div[8]/div/div/div[1]/div[2]/a"
            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            try:
                element.click()
            except:
                self.driver.execute_script("arguments[0].click();", element)
            logger.info("Clicked the breaking news redirect link.")
        except Exception as e:
            logger.error(f"Failed to click element: {str(e)}")

    def extract_breaking_news(self):
        logger.info("Extracting breaking news from redirected page...")
        try:
            WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.breaking-news ul li"))
            )
            time.sleep(2)
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            items = soup.select("div.breaking-news ul li")

            for li in items:
                time_tag = li.select_one("div.leftarea-inner span")
                news_tag = li.select_one("div.leftarea-inner div.content p")
                if time_tag and news_tag:
                    self.news_data.append({
                        "Time": time_tag.get_text(strip=True),
                        "News": news_tag.get_text(strip=True)
                    })

            logger.info(f"✅ Extracted {len(self.news_data)} news items.")
        except Exception as e:
            logger.error(f"Data extraction failed: {str(e)}")

    def save_to_excel(self):
        if not self.news_data:
            logger.warning("No data to save.")
            return
        os.makedirs("output", exist_ok=True)
        df = pd.DataFrame(self.news_data)
        filename = f"output/aajtak_breaking_news_{datetime.now():%d_%b_%Y_%H%M}.xlsx"
        df.to_excel(filename, index=False)
        logger.info(f"✅ Data saved to: {filename}")

    def run(self):
        try:
            self.open_and_click()
            self.extract_breaking_news()
            self.save_to_excel()
        finally:
            self.driver.quit()
            logger.info("Session ended")

if __name__ == "__main__":
    scraper = AajTakScraper()
    scraper.run()
