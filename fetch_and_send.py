import requests
import os
from datetime import datetime
from openai import OpenAI

# ── Config ──────────────────────────────────────────────
OPENAI_API_KEY    = os.environ["OPENAI_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]
# ────────────────────────────────────────────────────────

def get_ai_news() -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)
    today  = datetime.now().strftime("%d/%m/%Y")

    response = client.responses.create(
        model="gpt-4o",
        tools=[{"type": "web_search_preview"}],
        input=(
            f"Hôm nay là {today}. Hãy tìm kiếm và tổng hợp 5–7 tin tức AI "
            "nổi bật nhất trong 24 giờ qua từ các nguồn uy tín như TechCrunch, "
            "The Verge, Ars Technica, VentureBeat, OpenAI blog, Anthropic blog, "
            "Google DeepMind blog...\n\n"
            "Trả về ĐÚNG format sau (dùng Markdown cho Telegram):\n\n"
            f"🤖 *Tin tức AI - {today}*\n\n"
            "1\\. *[Tiêu đề tin]* — [1-2 câu tóm tắt ngắn gọn bằng tiếng Việt]\\. [Link nguồn]\n"
            "2\\. ...\n\n"
            "Chỉ trả về nội dung tin tức, không thêm lời mở đầu hay kết thúc."
        ),
    )

    return response.output_text.strip()


def send_telegram(message: str) -> bool:
    url     = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    r = requests.post(url, json=payload, timeout=15)
    return r.ok


def main():
    print("Đang tìm tin tức AI...")
    news = get_ai_news()

    if not news:
        print("Không lấy được tin tức.")
        return

    print("Đang gửi Telegram...")
    if send_telegram(news):
        print("✅ Gửi thành công!")
    else:
        print("❌ Gửi thất bại.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
