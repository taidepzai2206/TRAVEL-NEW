import requests
import feedparser
import google.generativeai as genai
import os

# =========================
# CONFIG
# =========================

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = "@taitravel"

# =========================
# GEMINI
# =========================

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# =========================
# RSS
# =========================

rss_urls = [
    "https://news.google.com/rss/search?q=Vietnam+tourism",
    "https://news.google.com/rss/search?q=Korea+tourism",
    "https://news.google.com/rss/search?q=Japan+tourism",
    "https://news.google.com/rss/search?q=Europe+tourism"
]

# =========================
# LẤY TIN
# =========================

for rss in rss_urls:
    feed = feedparser.parse(rss)

    if not feed.entries:
        continue

    article = feed.entries[0]

    prompt = f"""
Bạn là biên tập viên của một trang tin du lịch.

Viết bằng tiếng Việt.

Yêu cầu:
- Tiêu đề hấp dẫn
- Tóm tắt ngắn
- Nội dung khoảng 50-100 từ
- Văn phong chuyên nghiệp
- 3 hashtag

Tin:
{article.title}

Nguồn:
{article.link}
"""

    response = model.generate_content(prompt)

    content = f"""📰 {article.title}

{response.text}

🔗 {article.link}
"""

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": content[:4000]
        }
    )

    break

print("Done")
