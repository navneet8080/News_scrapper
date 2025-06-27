import logging
import time
import os
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aajtak_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === Main Automation Class ===
class AajTakScraper:
    def __init__(self):
        self.driver = self._setup_driver()
        self.news_data = []

    def _setup_driver(self):
        logger.info("✅ Setting up Chrome WebDriver")
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(10)
        return driver

    def open_and_click_news(self):
        logger.info("🌐 Navigating to AajTak homepage...")
        self.driver.get("https://www.aajtak.in")

        try:
            xpath = "/html/body/div[8]/div/div/div[1]/div[2]/a"
            logger.info(f"🔍 Waiting for clickable news element using XPath: {xpath}")
            element = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            element.click()
            logger.info("✅ Successfully clicked the news link.")
        except Exception as e:
            logger.error(f"❌ Failed to click news link: {str(e)}")
            self.driver.quit()
            raise

    def extract_news_with_bs4(self):
        try:
            logger.info("⏳ Waiting for breaking news section to load...")
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.breaking-news ul li"))
            )
            time.sleep(3)

            html = self.driver.page_source
            self.driver.quit()
            soup = BeautifulSoup(html, "html.parser")

            logger.info("🧾 Parsing HTML with BeautifulSoup")
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
            logger.error(f"❌ Failed to extract news: {str(e)}")

    def save_to_excel(self):
        if not self.news_data:
            logger.warning("⚠️ No news data to save.")
            return

        df = pd.DataFrame(self.news_data)
        os.makedirs("output", exist_ok=True)
        filename = f"output/aajtak_breaking_news_{datetime.now():%d_%b_%Y_%H%M}.xlsx"
        df.to_excel(filename, index=False)
        logger.info(f"💾 Saved news to: {filename}")

    def run(self):
        try:
            self.open_and_click_news()
            self.extract_news_with_bs4()
            self.save_to_excel()
        finally:
            if self.driver:
                self.driver.quit()
            logger.info("🔚 Session ended")

if __name__ == "__main__":
    scraper = AajTakScraper()
    scraper.run()