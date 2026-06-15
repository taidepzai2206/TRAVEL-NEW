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

article = None

# Lấy 1 bài đầu tiên hợp lệ
for rss in rss_urls:
    feed = feedparser.parse(rss)

    if not feed.entries:
        continue

    for entry in feed.entries[:5]:
        if entry.link not in sent_links:
            article = entry
            sent_links.add(entry.link)
            break

    if article:
        break

# Nếu không có bài
if not article:
    print("No article found")
    exit()

# =========================
# PROMPT VNEXPRESS STYLE
# =========================

prompt = f"""
Bạn là biên tập viên của tòa soạn báo du lịch chuyên nghiệp (VnExpress style).

Viết lại tin theo chuẩn báo chí tiếng Việt.

Yêu cầu:

1. TIÊU ĐỀ:
- Ngắn gọn, mạnh, tối đa 15 từ

2. SAPO (mở bài):
- 2–3 câu
- Tóm tắt nội dung chính
- Thu hút người đọc

3. NỘI DUNG:
- 2–3 đoạn ngắn
- Văn phong khách quan, báo chí
- Không dùng emoji trong nội dung

4. KẾT BÀI:
- 1 câu nhận định hoặc câu hỏi

5. ĐỘ DÀI:
- 120–170 từ

Tin:
{article.title}

Nguồn:
{article.link}
"""

# =========================
# GEMINI CALL (SAFE)
# =========================

try:
    response = model.generate_content(prompt)
    ai_text = response.text
except Exception as e:
    print("Gemini error:", e)
    ai_text = "Không thể tạo nội dung AI lúc này."

# =========================
# FORMAT TELEGRAM (VNEXPRESS STYLE)
# =========================

content = f"""
<b>📰 {article.title}</b>

━━━━━━━━━━━━━━

{ai_text}

━━━━━━━━━━━━━━

📌 Nguồn: <a href="{article.link}">Xem chi tiết</a>

#travel #news #vnexpress
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

print("Done")
