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
# RSS VISA
# =========================

rss_urls = [
    "https://news.google.com/rss/search?q=visa+update",
    "https://news.google.com/rss/search?q=immigration+policy",
    "https://news.google.com/rss/search?q=Japan+visa",
    "https://news.google.com/rss/search?q=Korea+visa",
    "https://news.google.com/rss/search?q=Schengen+visa"
]

# =========================
# LẤY BÀI
# =========================

article = None

for rss in rss_urls:
    feed = feedparser.parse(rss)

    if not feed.entries:
        continue

    article = feed.entries[0]
    break

if not article:
    print("No article")
    exit()

# =========================
# PROMPT
# =========================

prompt = f"""
Bạn là biên tập viên chuyên về visa và di trú quốc tế.

Viết lại tin theo phong cách báo chí.

- Tiêu đề rõ ràng
- Sapo 2-3 câu
- Nội dung 120-170 từ
- Giải thích chính sách visa
- Kết luận có câu hỏi

Tin:
{article.title}

Nguồn:
{article.link}
"""

# =========================
# GEMINI
# =========================

try:
    response = model.generate_content(prompt)
    text = response.text
except:
    text = "Không tạo được nội dung"

# =========================
# TELEGRAM
# =========================

content = f"""
🛂 VISA UPDATE

━━━━━━━━━━━━━━

{text}

━━━━━━━━━━━━━━

🔗 {article.link}
"""

requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": content[:4000]
    }
)

print("Done")
