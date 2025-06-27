import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def run_google_news_scraper():
    logger.info("📰 Starting Google News Hindi (भारत) Scraper...")

    # Chrome options
    options = Options()
    options.add_argument("--start-maximized")

    # Start WebDriver
    driver = webdriver.Chrome(options=options)
    driver.get("https://news.google.com/home?hl=hi&gl=IN&ceid=IN:hi")
    logger.info("🌐 Opened Google News Homepage")

    time.sleep(8)  # Wait for full load

    try:
        # Click "भारत" tab
        bharat_tab = driver.find_element(By.XPATH, '/html/body/div[4]/header/div[3]/div/c-wiz/div[1]/div[6]/a')
        bharat_tab.click()
        logger.info("✅ Clicked on भारत tab")
    except Exception as e:
        logger.warning("❌ Failed to click भारत tab with XPath, trying fallback...")
        try:
            driver.find_element(By.LINK_TEXT, "भारत").click()
        except Exception as e:
            logger.error("🔥 Fallback also failed. Exiting...")
            driver.quit()
            return

    time.sleep(5)

    # Scroll to load more cards
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    # Parse content
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    news_cards = soup.find_all("a", class_="gPFEn")
    logger.info(f"🔍 Found {len(news_cards)} news items.")

    news_data = []
    for card in news_cards:
        title = card.get_text(strip=True)
        href = card.get("href")
        if title and href:
            link = "https://news.google.com" + href[1:] if href.startswith(".") else href
            news_data.append({
                "Title": title,
                "Link": link
            })

    if not news_data:
        logger.warning("⚠️ No news data extracted.")
        return

    df = pd.DataFrame(news_data)
    filename = f"output/google_news_bharat_{datetime.now():%d_%b_%Y_%H%M}.xlsx"
    df.to_excel(filename, index=False)
    logger.info(f"✅ News saved to {filename}")
    print(df.head(10))

if __name__ == "__main__":
    run_google_news_scraper()
