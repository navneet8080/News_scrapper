import time
import logging
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("output/ani_scraper.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_ani_scraper():
    logger.info("Scraping ANI National News...")

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    
    driver = uc.Chrome(options=options)

    url = "https://aninews.in/category/national/"
    logger.info(f"Visiting: {url}")
    driver.get(url)

    logger.info("Waiting for Cloudflare challenge to clear if present...")

    try:
        # Try manually clicking Cloudflare checkbox if it appears
        time.sleep(3)
        checkbox = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/label/input")
        driver.execute_script("arguments[0].click();", checkbox)
        logger.info("Clicked Cloudflare checkbox.")
        time.sleep(5)
    except Exception:
        logger.info("No manual challenge detected.")

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "figcaption"))
        )
    except Exception as e:
        logger.error(f"Failed to load content: {str(e)}")
        driver.quit()
        return

    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    news_data = []
    items = soup.select("figcaption")

    for fig in items:
        try:
            time_tag = fig.select_one("p.time")
            title_tag = fig.select_one("a > h6.title")
            desc_tag = fig.select_one("p.text")

            if time_tag and title_tag and desc_tag:
                news_data.append({
                    "Time": time_tag.get_text(strip=True),
                    "Title": title_tag.get_text(strip=True),
                    "Description": desc_tag.get_text(strip=True)
                })
        except Exception:
            continue

    if not news_data:
        logger.warning("No data extracted from ANI page.")
        return

    df = pd.DataFrame(news_data)
    filename = f"output/ani_national_{datetime.now():%d_%b_%Y_%H%M}.xlsx"
    df.to_excel(filename, index=False)
    logger.info(f"Saved ANI news to: {filename}")

if __name__ == "__main__":
    run_ani_scraper()