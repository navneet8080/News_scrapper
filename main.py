from scrapers.aajtak_scraper import AajTakScraper
from scrapers.latestly_scraper import scrape_latestly
from scrapers.ani_scraper import run_ani_scraper
from scrapers.googlenews_scrapper import run_google_news_scraper
from scrapers.hindusthan_scrapper import main as hindustan_scrape
from utils.combiner import combine_all_outputs
from ai.ai_summ import main as run_summarizer


if __name__ == "__main__":
    print("🔄 Running all scrapers...")

    AajTakScraper().run()
    scrape_latestly()
    run_ani_scraper()
    run_google_news_scraper()
    hindustan_scrape()

    print("🧩 Combining all Excel outputs...")
    try:
        combined_path = combine_all_outputs()
        if combined_path:
            print(f"✅ Combined file ready at: {combined_path}")
        else:
            print("⚠️ No data to combine.")
    except Exception as e:
        print(f"❌ Error during combining: {e}")

    run_summarizer()
    print("sucesssssss")