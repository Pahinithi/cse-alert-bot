import json
import os
import re

ALERTS_FILE = "custom_alerts.json"
OFFSET_FILE = "telegram_offset.json"


def load_alerts() -> list:
    if not os.path.exists(ALERTS_FILE):
        return []
    try:
        with open(ALERTS_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def save_alerts(alerts: list):
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)


def load_offset() -> int:
    if not os.path.exists(OFFSET_FILE):
        return 0
    try:
        with open(OFFSET_FILE) as f:
            return json.load(f).get("offset", 0)
    except Exception:
        return 0


def save_offset(offset: int):
    with open(OFFSET_FILE, "w") as f:
        json.dump({"offset": offset}, f)


def _parse_command(text: str) -> dict:
    text = text.strip()

    # /alert SYMBOL below/above PRICE
    match = re.match(r"/alert\s+(\S+)\s+(below|above)\s+([\d.]+)", text, re.IGNORECASE)
    if match:
        return {
            "command": "alert",
            "symbol": match.group(1).upper(),
            "condition": match.group(2).lower(),
            "price": float(match.group(3)),
        }

    if text.lower() in ("/list", "/list@cse_alert_bot"):
        return {"command": "list"}

    match = re.match(r"/remove\s+(\S+)", text, re.IGNORECASE)
    if match:
        return {"command": "remove", "symbol": match.group(1).upper()}

    if text.lower().startswith("/help"):
        return {"command": "help"}

    return {"command": "unknown", "raw": text}


HELP_TEXT = (
    "CSE Alert Bot Commands\n\n"
    "/alert SYMBOL below PRICE\n"
    "  Send alert when price drops below target\n"
    "  Example: /alert LOLC.N0000 below 500\n\n"
    "/alert SYMBOL above PRICE\n"
    "  Send alert when price rises above target\n"
    "  Example: /alert COMB.N0000 above 220\n\n"
    "/list\n"
    "  Show all your active price alerts\n\n"
    "/remove SYMBOL\n"
    "  Remove alerts for a stock\n"
    "  Example: /remove LOLC.N0000\n\n"
    "/help\n"
    "  Show this message"
)


def process_updates(updates: list, token: str, chat_id: str, notifier_fn) -> int:
    """
    Process new Telegram messages and handle commands.
    Returns the new offset to use on the next call.
    """
    if not updates:
        return load_offset()

    alerts = load_alerts()
    max_update_id = load_offset()

    for update in updates:
        update_id = update.get("update_id", 0)
        if update_id < max_update_id:
            continue
        max_update_id = max(max_update_id, update_id)

        message = update.get("message", {})
        text = message.get("text", "")
        if not text or not text.startswith("/"):
            continue

        cmd = _parse_command(text)

        if cmd["command"] == "alert":
            symbol = cmd["symbol"]
            condition = cmd["condition"]
            price = cmd["price"]

            # Replace existing alert for same symbol + condition
            alerts = [
                a
                for a in alerts
                if not (a["symbol"] == symbol and a["condition"] == condition)
            ]
            alerts.append({"symbol": symbol, "condition": condition, "price": price})
            save_alerts(alerts)

            notifier_fn(
                token,
                chat_id,
                f"Alert set\n\n"
                f"<b>{symbol}</b> {condition} Rs {price:.2f}\n"
                f"You will be notified when this condition is triggered.\n"
                f"Use /list to see all your active alerts.",
            )

        elif cmd["command"] == "list":
            alerts = load_alerts()
            if not alerts:
                notifier_fn(
                    token,
                    chat_id,
                    "You have no active price alerts.\n\nUse /help to see how to set one.",
                )
            else:
                lines = ["<b>Active Price Alerts:</b>\n"]
                for a in alerts:
                    lines.append(
                        f"  {a['symbol']}  {a['condition']}  Rs {a['price']:.2f}"
                    )
                notifier_fn(token, chat_id, "\n".join(lines))

        elif cmd["command"] == "remove":
            symbol = cmd["symbol"]
            before = len(alerts)
            alerts = [a for a in alerts if a["symbol"] != symbol]
            save_alerts(alerts)
            if len(alerts) < before:
                notifier_fn(token, chat_id, f"Removed all alerts for <b>{symbol}</b>.")
            else:
                notifier_fn(
                    token, chat_id, f"No active alerts found for <b>{symbol}</b>."
                )

        elif cmd["command"] == "help":
            notifier_fn(token, chat_id, HELP_TEXT)

        else:
            notifier_fn(
                token,
                chat_id,
                f"Unknown command: {cmd.get('raw', text)}\n\nSend /help to see available commands.",
            )

    new_offset = max_update_id + 1
    save_offset(new_offset)
    return new_offset


def check_custom_alerts(token: str, chat_id: str, notifier_fn) -> list:
    """
    Check all saved custom price alerts against live CSE prices.
    Sends a Telegram message for each triggered alert.
    Removes triggered alerts from the saved list.
    Returns list of triggered symbols.
    """
    from cse_api import get_company_info

    alerts = load_alerts()
    triggered = []
    remaining = []

    for alert in alerts:
        symbol = alert["symbol"]
        condition = alert["condition"]
        target = alert["price"]

        data, error = get_company_info(symbol)
        if error:
            print(f"Could not fetch price for {symbol}: {error}")
            remaining.append(alert)
            continue

        price = data.get("last_traded_price")
        if not isinstance(price, (int, float)):
            remaining.append(alert)
            continue

        is_triggered = (condition == "below" and price <= target) or (
            condition == "above" and price >= target
        )

        if is_triggered:
            change_pct = data.get("change_pct", "N/A")
            change_str = (
                f"{change_pct:+.2f}%"
                if isinstance(change_pct, (int, float))
                else str(change_pct)
            )

            notifier_fn(
                token,
                chat_id,
                f"PRICE ALERT TRIGGERED\n\n"
                f"<b>{symbol}</b>\n"
                f"{data.get('name', '')}\n\n"
                f"Your target : {condition} Rs {target:.2f}\n"
                f"Current price: Rs {price:.2f}\n"
                f"Change today : {change_str}\n\n"
                f"This alert has been removed.",
            )
            triggered.append(symbol)
        else:
            remaining.append(alert)

    if triggered:
        save_alerts(remaining)

    return triggered
