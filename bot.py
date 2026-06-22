python
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
# GEMINI SETUP
# =========================

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# =========================
# RSS SOURCES
# =========================

rss_urls = [
    "https://news.google.com/rss/search?q=Vietnam+tourism",
    "https://news.google.com/rss/search?q=travel+industry",
    "https://news.google.com/rss/search?q=tourism+trend",
    "https://news.google.com/rss/search?q=Japan+tourism",
    "https://news.google.com/rss/search?q=Korea+tourism",
    "https://news.google.com/rss/search?q=aviation+travel"
]

# =========================
# GET ARTICLE
# =========================

article = None

for rss in rss_urls:
    feed = feedparser.parse(rss)

    if not feed.entries:
        continue

    article = feed.entries[0]
    break

if not article:
    print("No article found")
    exit()

# =========================
# PROMPT
# =========================

prompt = f"""
Bạn là:

1. Biên tập viên du lịch chuyên nghiệp.
2. Content Creator chuyên làm TikTok, Reels và Facebook về du lịch.

Từ tin tức dưới đây hãy tạo bài đăng theo đúng cấu trúc:

=========================
📰 TIN DU LỊCH
=========================

TIÊU ĐỀ:
(Tạo tiêu đề hấp dẫn)

SAPO:
(2-3 câu tóm tắt)

NỘI DUNG:
(100-120 từ, văn phong giống VnExpress)

KẾT LUẬN:
(1 câu nhận định hoặc câu hỏi)

=========================
🎬 GÓC CONTENT CREATOR
=========================

HOOK:
(1 câu cực thu hút)

TIÊU ĐỀ VIDEO:
(ngắn gọn, dễ viral)

VOICE OVER:
(Kịch bản đọc khoảng 45-60 giây)

SHOT LIST GỢI Ý:
1. ...
2. ...
3. ...
4. ...
5. ...

CAPTION FACEBOOK/TIKTOK:
(ngắn gọn, dễ tương tác)

HASHTAG:
#dulich #travel #tourism #tintuc #viral

=========================

Tin gốc:
{article.title}

Nguồn:
{article.link}
"""

# =========================
# GEMINI
# =========================

try:
    response = model.generate_content(prompt)
    ai_text = response.text

except Exception as e:
    print("Gemini error:", e)

    ai_text = f"""
📰 TIN DU LỊCH

{article.title}

Hiện Gemini đang hết quota hoặc gặp lỗi.

🎬 GÓC CONTENT CREATOR

HOOK:
Tin nóng ngành du lịch hôm nay!

📌 Nguồn:
{article.link}
"""

# =========================
# TELEGRAM FORMAT
# =========================

content = f"""
🌍 <b>TRAVEL NEWS & CONTENT</b>

━━━━━━━━━━━━━━

{ai_text}

━━━━━━━━━━━━━━

📌 <a href="{article.link}">Nguồn bài viết</a>
"""

# =========================
# SEND TELEGRAM
# =========================

response = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": content[:4000],
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
)

print("Telegram Status:", response.status_code)
print("Done")
