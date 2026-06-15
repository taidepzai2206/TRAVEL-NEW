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
    "https://news.google.com/rss/search?q=Korea+tourism",
    "https://news.google.com/rss/search?q=Japan+tourism",
    "https://news.google.com/rss/search?q=Europe+tourism"
]

# =========================
# CHỐNG TRÙNG
# =========================

sent_links = set()

# =========================
# MAIN
# =========================

for rss in rss_urls:
    feed = feedparser.parse(rss)

    if not feed.entries:
        continue

    for article in feed.entries[:5]:

        if article.link in sent_links:
            continue

        sent_links.add(article.link)

        # =========================
        # PROMPT AI (PRO STYLE)
        # =========================

        prompt = f"""
Bạn là biên tập viên của một trang báo du lịch quốc tế.

Viết bài bằng tiếng Việt.

Yêu cầu:
- Tiêu đề hấp dẫn như báo điện tử
- Mở bài có hook thu hút người đọc
- Nội dung 120–180 từ
- Văn phong tự nhiên, không giống AI
- Có góc nhìn du lịch thực tế
- Chia đoạn rõ ràng
- Kết thúc bằng 1 câu hỏi tương tác
- Thêm 3 hashtag liên quan du lịch

Tin gốc:
{article.title}

Nguồn:
{article.link}
"""

        response = model.generate_content(prompt)

        # =========================
        # FORMAT TELEGRAM (VNEXPRESS STYLE)
        # =========================

        content = f"""
<b>📰 {article.title}</b>

━━━━━━━━━━━━━━
{response.text}
━━━━━━━━━━━━━━

🔗 <a href="{article.link}">Xem nguồn bài viết</a>

#travel #news #vietnam
"""

        # =========================
        # SEND TELEGRAM
        # =========================

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": content[:4000],
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
        )

        # chỉ gửi 1 bài mỗi lần chạy
        break

print("Done")
