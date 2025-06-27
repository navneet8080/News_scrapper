import time, os
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def scrape_latestly():
    print("🔍 Scraping LatestLY...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = "https://hindi.latestly.com/quickly/"
    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    news_items = soup.select("section.category-cards-list ul li")
    print(f"📦 Found {len(news_items)} news items.")

    news_data = []
    for item in news_items:
        link_tag = item.select_one("a")
        title_tag = item.select_one("h3")
        if link_tag and title_tag:
            news_data.append({
                "Title": title_tag.get_text(strip=True),
                "Link": link_tag['href']
            })

    df = pd.DataFrame(news_data)
    os.makedirs("output", exist_ok=True)
    filename = f"output/latestly_quickly_{datetime.now():%d_%b_%Y_%H%M}.xlsx"
    df.to_excel(filename, index=False)
    print(f"✅ Data saved to: {filename}")
    return df
if __name__ == "__main__":
    a = scrape_latestly()
