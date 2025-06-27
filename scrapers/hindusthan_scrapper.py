
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime

def extract_news(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    news_items = soup.find_all("div", class_="smptblog-design")
    
    data = []
    for item in news_items:
        try:
            title_tag = item.find("h1").find("a")
            title = title_tag.text.strip()
            link = "https://www.hindusthansamachar.in" + title_tag['href'].replace("//", "/")

            desc_tag = item.find("p").find("a")
            description = desc_tag.text.strip()

            image_div = item.find("div", class_="image")
            style = image_div.get("style")
            image_url = style.split("url(")[1].split(")")[0].replace('"', '')

            data.append({
                "Title": title,
                "Description": description,
                "Link": link,
                "Image": image_url
            })
        except Exception as e:
            continue
    return data

def main():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    
    news_data = []

    urls = [
        "https://www.hindusthansamachar.in/national.php",
        "https://www.hindusthansamachar.in/uttar-pradesh.php",
        "https://www.hindusthansamachar.in/sport.php"
        
    ]

    for url in urls:
        print(f"🌐 Visiting: {url}")
        driver.get(url)
        time.sleep(5)
        news_data.extend(extract_news(driver))

    driver.quit()

    df = pd.DataFrame(news_data)
    filename = f"output/hindusthan_{datetime.now():%d_%b_%Y_%H%M}.xlsx"
    df.to_excel(filename, index=False)
    print(f"✅ Data saved to {filename}")

if __name__ == "__main__":
    main()
