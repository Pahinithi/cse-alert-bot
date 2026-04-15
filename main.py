import os
import sys
from datetime import datetime

try:
    import pytz

    SL_TZ = pytz.timezone("Asia/Colombo")

    def now_sl():
        return datetime.now(SL_TZ)
except ImportError:
    # Fallback: GitHub Actions runs in UTC, offset manually
    from datetime import timezone, timedelta

    SL_OFFSET = timedelta(hours=5, minutes=30)

    def now_sl():
        return datetime.now(timezone.utc) + SL_OFFSET


import config
from notifier import send_message, get_updates
from alert_engine import check_market_alerts, send_daily_summary
from custom_alerts import load_offset, process_updates, check_custom_alerts


def is_market_open() -> bool:
    now = now_sl()
    if hasattr(now, "weekday"):
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
    open_h, open_m = config.MARKET_OPEN_HOUR, config.MARKET_OPEN_MIN
    close_h, close_m = config.MARKET_CLOSE_HOUR, config.MARKET_CLOSE_MIN
    now_minutes = now.hour * 60 + now.minute
    open_minutes = open_h * 60 + open_m
    close_minutes = close_h * 60 + close_m
    return open_minutes <= now_minutes <= close_minutes


def is_market_just_opened() -> bool:
    now = now_sl()
    return (
        now.hour == config.MARKET_OPEN_HOUR and now.minute < 35  # within 35 min of open
    )


def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("ERROR: Set TELEGRAM_TOKEN and TELEGRAM_CHAT_ID in GitHub Secrets.")
        sys.exit(1)

    now = now_sl()
    print(f"Running at {now.strftime('%Y-%m-%d %H:%M')} Sri Lanka time")
    print(f"Market open: {is_market_open()}")

    # Step 1: Process Telegram commands (always, even outside hours) ─
    print("Checking Telegram for new commands...")
    offset = load_offset()
    updates = get_updates(token, offset=offset)
    process_updates(updates, token, chat_id, send_message)

    # Step 2: Skip market checks if market is closed
    if not is_market_open():
        print("Market is closed. Skipping market checks.")
        return

    # Step 3: Send daily summary at market open
    if config.SEND_DAILY_SUMMARY and is_market_just_opened():
        print("Sending daily market summary...")
        send_daily_summary(token, chat_id, send_message)

    # Step 4: Check automatic market alerts ─
    print("Checking automatic market alerts...")
    triggered = check_market_alerts(token, chat_id, send_message)
    if triggered:
        print(f"Sent alerts: {triggered}")
    else:
        print("No automatic alerts triggered.")

    # Step 5: Check custom user price alerts
    print("Checking custom price alerts...")
    triggered_custom = check_custom_alerts(token, chat_id, send_message)
    if triggered_custom:
        print(f"Custom alerts triggered: {triggered_custom}")
    else:
        print("No custom price alerts triggered.")

    print("Done.")


if __name__ == "__main__":
    main()
