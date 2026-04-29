import requests
import os
from datetime import datetime
from openai import OpenAI

# ── Config ──────────────────────────────────────────────
GITHUB_TOKEN       = os.environ["GITHUB_TOKEN"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]
# ────────────────────────────────────────────────────────

def get_ai_news() -> str:
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=GITHUB_TOKEN,
    )
    today = datetime.now().strftime("%d/%m/%Y")

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2000,
        messages=[
            {
                "role": "system",
                "content": "Bạn là trợ lý tổng hợp tin tức AI. Hãy tìm và tổng hợp tin tức AI mới nhất."
            },
            {
                "role": "user",
                "content": (
                    f"Hôm nay là {today}. Hãy tổng hợp 5–7 tin tức AI "
                    "nổi bật nhất trong 24 giờ qua từ các nguồn uy tín như TechCrunch, "
                    "The Verge, Ars Technica, VentureBeat, OpenAI blog, Anthropic blog, "
                    "Google DeepMind blog.\n\n"
                    "Trả về ĐÚNG format sau (Markdown cho Telegram):\n\n"
                    f"🤖 *Tin tức AI \\- {today}*\n\n"
                    "1\\. *Tiêu đề tin* \\— Tóm tắt 1\\-2 câu bằng tiếng Việt\\. [Nguồn](link)\n"
                    "2\\. \\.\\.\\.\n\n"
                    "Chỉ trả về nội dung, không thêm lời mở đầu hay kết thúc\\."
                ),
            }
        ],
    )

    return response.choices[0].message.content.strip()


def send_telegram(message: str) -> bool:
    url     = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True,
    }
    r = requests.post(url, json=payload, timeout=15)
    if not r.ok:
        # Fallback: gửi plain text nếu Markdown lỗi
        payload["parse_mode"] = None
        r = requests.post(url, json=payload, timeout=15)
    return r.ok


def main():
    print("Đang tìm tin tức AI...")
    news = get_ai_news()
    print("Nội dung:\n", news)

    if not news:
        print("Không lấy được tin tức.")
        return

    print("\nĐang gửi Telegram...")
    if send_telegram(news):
        print("✅ Gửi thành công!")
    else:
        print("❌ Gửi thất bại.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
