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
# CHỐNG GỬI TIN TRÙNG
# =========================

sent_links = set()

# =========================
# MAIN LOOP
# =========================

for rss in rss_urls:
    feed = feedparser.parse(rss)

    if not feed.entries:
        continue

    # lấy tối đa 5 bài để tránh spam + tăng cơ hội bài mới
    for article in feed.entries[:5]:

        if article.link in sent_links:
            continue

        sent_links.add(article.link)

        prompt = f"""
Bạn là biên tập viên du lịch chuyên nghiệp.

Viết bài tin tức du lịch bằng tiếng Việt.

Yêu cầu:
- Tiêu đề hấp dẫn như báo điện tử
- Mở bài có hook thu hút
- Nội dung 50–100 từ
- Văn phong tự nhiên, không giống AI
- Có góc nhìn du lịch thực tế
- Kết thúc bằng 1 câu hỏi tương tác
- Thêm 3 hashtag

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

        # chỉ gửi 1–2 bài mỗi lần chạy để tránh spam
        break

print("Done")
