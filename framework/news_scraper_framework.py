# framework/news_scraper_framework.py
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

class NewsScraperFramework:
    def __init__(self, site_name, driver, logger):
        self.site_name = site_name
        self.driver = driver
        self.logger = logger
        self.news_data = []

    def load_page(self, url):
        self.logger.info(f"🌐 Visiting: {url}")
        self.driver.get(url)
        time.sleep(5)  # Wait for JS to render
        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")

    def extract_news(self, item_selector, title_selector, link_selector):
        items = self.soup.select(item_selector)
        self.logger.info(f"📰 Found {len(items)} news items.")

        for item in items:
            title_tag = item.select_one(title_selector)
            link_tag = item.select_one(link_selector)
            if title_tag and link_tag:
                self.news_data.append({
                    "Title": title_tag.get_text(strip=True),
                    "Link": link_tag['href']
                })

    def save_to_excel(self):
        if not self.news_data:
            self.logger.warning("No news data to save.")
            return None

        df = pd.DataFrame(self.news_data)
        filename = f"output/{self.site_name}_{datetime.now():%d_%b_%Y_%H%M}.xlsx"
        df.to_excel(filename, index=False)
        self.logger.info(f"✅ Saved to: {filename}")
        return df.head(5)
