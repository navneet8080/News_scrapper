# import requests
# import json
# import pandas as pd
# from datetime import datetime
# from pathlib import Path

# # 🔧 Configuration
# API_KEY = "AIzaSyCDLW5oGmEziI1J9HdHqkH_jGR0pgJAtMY"  # <-- 🔁 Paste your actual API Key here
# MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# INPUT_DIR = Path("combined")
# OUTPUT_DIR = Path("output")
# TIMESTAMP = datetime.now().strftime("%d_%b_%Y_%H%M")
# OUTPUT_FILE = OUTPUT_DIR / f"summary_{TIMESTAMP}.txt"

# def get_latest_excel():
#     files = sorted(INPUT_DIR.glob("*.xlsx"), key=lambda x: x.stat().st_mtime, reverse=True)
#     if not files:
#         raise FileNotFoundError("❌ No input Excel file found in 'combined' directory.")
#     return files[0]

# def build_prompt(news_list):
#     prompt = (
#         "आपके पास विभिन्न समाचार स्रोतों से प्राप्त 300 समाचार शीर्षकों की एक सूची है। कृपया नीचे दिए गए शीर्षकों में से "
#         "50 सबसे महत्वपूर्ण, अद्वितीय और ताज़ा समाचार चुनें। हर समाचार को 7 से 8 शब्दों में संक्षेप में एकदम स्पष्ट, प्रभावशाली "
#         "और ब्रेकिंग न्यूज़ शैली में हिंदी में लिखें।\n\n➡️ ध्यान दें:\n"
#         "1. केवल वही समाचार चुनें जो अद्वितीय हों — एक जैसी या दोहराए गए शीर्षकों को हटा दें।\n"
#         "2. हर हेडलाइन छोटे वाक्य के रूप में होनी चाहिए, जैसे कि टीवी पर चलने वाले ब्रेकिंग न्यूज़ फ्लैश।\n"
#         "3. कोई भूमिका या स्पष्टीकरण न दें, केवल 1 से 50 तक अंकित हेडलाइन सूची के रूप में उत्तर दें।\n"
#         "4. आउटपुट केवल हेडलाइन हो — बीच में कोई नोट, अनुच्छेद या विवरण न हो।\n"
#         "5. सभी हेडलाइन पूर्णतः हिंदी भाषा में होनी चाहिए, अंग्रेज़ी शब्द न हों।\n\n"
#         "समाचार शीर्षक:\n"
#     )
#     for idx, news in enumerate(news_list[:300], 1):
#         prompt += f"{idx}. {news.strip()}\n"
#     return prompt

# def call_gemini_api(prompt_text):
#     headers = {"Content-Type": "application/json"}
#     payload = {
#         "contents": [
#             {
#                 "parts": [
#                     {
#                         "text": prompt_text
#                     }
#                 ]
#             }
#         ]
#     }
#     response = requests.post(MODEL_URL, headers=headers, data=json.dumps(payload))
#     response.raise_for_status()
#     result = response.json()
#     return result["candidates"][0]["content"]["parts"][0]["text"]

# def main():
#     print("📂 Loading Excel file...")
#     excel_path = get_latest_excel()
#     df = pd.read_excel(excel_path)
#     news_list = df["news"].dropna().tolist()

#     print("🧠 Generating prompt for Gemini API...")
#     final_prompt = build_prompt(news_list)

#     print("🚀 Sending request to Gemini model...")
#     result = call_gemini_api(final_prompt)

#     OUTPUT_DIR.mkdir(exist_ok=True)
#     OUTPUT_FILE.write_text(result, encoding="utf-8")
#     print(f"✅ Headlines saved at: {OUTPUT_FILE}")

# if __name__ == "__main__":
#     main()


import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

# ==== CONFIGURATION ====
API_KEY = "AIzaSyCDLW5oGmEziI1J9HdHqkH_jGR0pgJAtMY"  # Replace with your actual API key
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
COMBINED_DIR = Path("combined")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


# ==== FUNCTIONS ====
def load_latest_news_file():
    files = sorted(COMBINED_DIR.glob("*.xlsx"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError("❌ No combined Excel file found.")
    return pd.read_excel(files[0])

def prepare_news_block(news_list):
    return "\n".join([f"{i+1}. {title}" for i, title in enumerate(news_list)])

def build_prompt(news_block):
    return f"""
आपके पास विभिन्न समाचार स्रोतों से प्राप्त 300 समाचार शीर्षकों की एक सूची है। कृपया इन शीर्षकों का विश्लेषण करके 50 सबसे महत्वपूर्ण, ताज़ा, और अद्वितीय समाचारों को चुनें और उन्हें अलग-अलग श्रेणियों में वर्गीकृत करें।

📌 निर्देश:

1. कुल 50 शीर्षक तैयार करें और उन्हें नीचे दी गई श्रेणियों में बाँटें:
   - 🏛️ राष्ट्रीय
   - 🌍 अंतरराष्ट्रीय
   - 🏛️ उत्तर प्रदेश
   - 🗳️ राजनीति
   - 🏏 खेल
   - 🌐 तकनीक/व्यापार/अन्य

2. प्रत्येक शीर्षक ब्रेकिंग न्यूज़ की शैली में स्पष्ट और प्रभावशाली हो। लंबाई अधिकतम 12 शब्दों तक हो।

3. केवल मूलभूत तथ्य रखें — विश्लेषण, विवरण या स्पष्टीकरण शामिल न करें।

4. दोहराए गए या मिलते-जुलते शीर्षकों को हटाएं।

5. उत्तर केवल निम्न फॉर्मेट में दें:

राष्ट्रीय:
1. <हेडलाइन>
2. <हेडलाइन>
...

6. सभी हेडलाइन पूरी तरह से हिंदी में हों, अंग्रेज़ी शब्दों का उपयोग न करें।

📰 कृपया नीचे दिए गए समाचार शीर्षकों को पढ़ें और ऊपर दिए निर्देशों के अनुसार उत्तर दें:

{news_block}
"""

def call_gemini_api(prompt_text):
    response = requests.post(
        GEMINI_URL, headers={"Content-Type": "application/json"}, json={"contents": [{"parts": [{"text": prompt_text}]}]}
    )
    if response.status_code != 200:
        raise Exception(f"Gemini API Error: {response.status_code} - {response.text}")
    candidates = response.json().get("candidates", [])
    return candidates[0]['content']['parts'][0]['text'] if candidates else "❌ कोई उत्तर नहीं मिला।"


# ==== MAIN ====
def main():
    print("📂 Loading latest news titles...")
    df = load_latest_news_file()
    headlines = df["news"].dropna().astype(str).tolist()[:300]
    news_block = prepare_news_block(headlines)

    print("✍️ Preparing structured prompt for Gemini...")
    prompt = build_prompt(news_block)

    print("🔗 Sending prompt to Gemini API...")
    result = call_gemini_api(prompt)

    timestamp = datetime.now().strftime("%d_%b_%Y_%H%M")
    out_file = OUTPUT_DIR / f"summary_{timestamp}.txt"
    out_file.write_text(result, encoding="utf-8")

    print(f"✅ Summary saved to {out_file}")


if __name__ == "__main__":
    main()