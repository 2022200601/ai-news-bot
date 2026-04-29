import anthropic
import requests
import os
from datetime import datetime

# ── Config ──────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
# ────────────────────────────────────────────────────────

def get_ai_news() -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    today = datetime.now().strftime("%d/%m/%Y")

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[
            {
                "role": "user",
                "content": (
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
            }
        ],
    )

    # Extract text from response (may include tool_use blocks)
    text_parts = [block.text for block in response.content if block.type == "text"]
    return "\n".join(text_parts).strip()


def send_telegram(message: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    response = requests.post(url, json=payload, timeout=15)
    return response.ok


def main():
    print("Đang tìm tin tức AI...")
    news = get_ai_news()

    if not news:
        print("Không lấy được tin tức.")
        return

    print("Đang gửi Telegram...")
    success = send_telegram(news)

    if success:
        print("✅ Gửi thành công!")
    else:
        print("❌ Gửi thất bại.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
