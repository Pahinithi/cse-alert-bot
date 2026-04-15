import requests

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


def send_message(token: str, chat_id: str, text: str) -> bool:
    url = TELEGRAM_API.format(token=token, method="sendMessage")
    try:
        r = requests.post(
            url,
            data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        if not r.ok:
            print(f"Telegram error {r.status_code}: {r.text[:200]}")
        return r.ok
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        return False


def get_updates(token: str, offset: int = 0) -> list:
    url = TELEGRAM_API.format(token=token, method="getUpdates")
    try:
        r = requests.get(
            url,
            params={"offset": offset, "timeout": 5},
            timeout=15,
        )
        if r.ok:
            return r.json().get("result", [])
        return []
    except Exception as e:
        print(f"Failed to get Telegram updates: {e}")
        return []
