import config
from cse_api import get_market_summary, get_all_sectors, get_top_gainers, get_top_losers
from tv_api import get_bulk_indicators


def check_market_alerts(token: str, chat_id: str, notifier_fn) -> list:
    """
    Run all automatic alert checks.
    Returns list of alert descriptions that were sent.
    """
    sent = []

    #  1. Significant gainers
    gainers, error = get_top_gainers(30)
    if not error:
        for stock in gainers:
            pct = stock.get("change_pct")
            if isinstance(pct, (int, float)) and pct >= config.GAIN_ALERT_PCT:
                qty = stock.get("qty", 0)
                qty_str = f"{int(qty):,}" if isinstance(qty, (int, float)) else str(qty)
                notifier_fn(
                    token,
                    chat_id,
                    f"SIGNIFICANT GAIN\n\n"
                    f"<b>{stock.get('symbol')}</b>\n"
                    f"{stock.get('name', '')}\n\n"
                    f"Up {pct:+.2f}% today\n"
                    f"Current Price : Rs {stock.get('price', 'N/A')}\n"
                    f"Volume        : {qty_str} shares",
                )
                sent.append(f"{stock.get('symbol')} +{pct:.1f}%")

    # 2. Significant losers
    losers, error = get_top_losers(30)
    if not error:
        for stock in losers:
            pct = stock.get("change_pct")
            if isinstance(pct, (int, float)) and pct <= -config.LOSS_ALERT_PCT:
                qty = stock.get("qty", 0)
                qty_str = f"{int(qty):,}" if isinstance(qty, (int, float)) else str(qty)
                notifier_fn(
                    token,
                    chat_id,
                    f"SIGNIFICANT LOSS\n\n"
                    f"<b>{stock.get('symbol')}</b>\n"
                    f"{stock.get('name', '')}\n\n"
                    f"Down {pct:+.2f}% today\n"
                    f"Current Price : Rs {stock.get('price', 'N/A')}\n"
                    f"Volume        : {qty_str} shares",
                )
                sent.append(f"{stock.get('symbol')} {pct:.1f}%")

    # 3. RSI signals for watchlist
    bulk, error = get_bulk_indicators(config.WATCHLIST, "1d")
    if not error:
        oversold = []
        overbought = []

        for symbol, data in bulk.items():
            rsi = data.get("rsi")
            if not isinstance(rsi, float):
                continue
            if rsi <= config.RSI_OVERSOLD:
                oversold.append((symbol, rsi, data.get("close")))
            elif rsi >= config.RSI_OVERBOUGHT:
                overbought.append((symbol, rsi, data.get("close")))

        if oversold:
            lines = ["RSI OVERSOLD ALERT\nPossible buy zone - RSI is very low\n"]
            for sym, rsi, close in oversold:
                price_str = f"Rs {close:.2f}" if isinstance(close, float) else "N/A"
                lines.append(f"<b>{sym}</b>   RSI={rsi:.1f}   Price={price_str}")
            notifier_fn(token, chat_id, "\n".join(lines))
            sent.extend([f"{s} RSI={r:.0f}" for s, r, _ in oversold])

        if overbought:
            lines = ["RSI OVERBOUGHT ALERT\nPossible sell zone - RSI is very high\n"]
            for sym, rsi, close in overbought:
                price_str = f"Rs {close:.2f}" if isinstance(close, float) else "N/A"
                lines.append(f"<b>{sym}</b>   RSI={rsi:.1f}   Price={price_str}")
            notifier_fn(token, chat_id, "\n".join(lines))
            sent.extend([f"{s} RSI={r:.0f}" for s, r, _ in overbought])

    # 4. ASPI movement
    summary, error = get_market_summary()
    if not error and summary and len(summary) >= 2:
        today_asi = summary[0].get("asi")
        prev_asi = summary[1].get("asi")

        if (
            isinstance(today_asi, (int, float))
            and isinstance(prev_asi, (int, float))
            and prev_asi > 0
        ):
            change_pct = ((today_asi - prev_asi) / prev_asi) * 100

            if abs(change_pct) >= config.ASPI_CHANGE_PCT:
                direction = "UP" if change_pct > 0 else "DOWN"
                turnover = summary[0].get("market_turnover", 0)
                tv_str = (
                    f"LKR {turnover / 1e9:.2f}B"
                    if isinstance(turnover, (int, float))
                    else "N/A"
                )

                notifier_fn(
                    token,
                    chat_id,
                    f"ASPI {direction} ALERT\n\n"
                    f"ASPI: {today_asi:,.2f}\n"
                    f"Change: {change_pct:+.2f}%\n"
                    f"Previous Close: {prev_asi:,.2f}\n"
                    f"Market Turnover: {tv_str}",
                )
                sent.append(f"ASPI {change_pct:+.1f}%")

    return sent


def send_daily_summary(token: str, chat_id: str, notifier_fn):
    """
    Send a full market overview at market open.
    """
    lines = ["CSE MARKET OPEN - Daily Summary\n"]

    # Market indices
    summary, error = get_market_summary()
    if not error and summary:
        today = summary[0]
        asi = today.get("asi", "N/A")
        sp = today.get("sp_sl20", "N/A")
        turnover = today.get("market_turnover", 0)
        trades = today.get("market_trades", "N/A")
        tv_str = (
            f"LKR {turnover / 1e9:.2f}B"
            if isinstance(turnover, (int, float))
            else "N/A"
        )

        lines.append(
            f"ASPI     : {asi:,}"
            if isinstance(asi, (int, float))
            else f"ASPI     : {asi}"
        )
        lines.append(
            f"S&P SL20 : {sp:,}" if isinstance(sp, (int, float)) else f"S&P SL20 : {sp}"
        )
        lines.append(f"Turnover : {tv_str}")
        lines.append(
            f"Trades   : {int(trades):,}"
            if isinstance(trades, (int, float))
            else f"Trades   : {trades}"
        )
        lines.append("")

    # Top gainers
    gainers, error = get_top_gainers(config.TOP_MOVERS_COUNT)
    if not error and gainers:
        lines.append("<b>Top Gainers:</b>")
        for s in gainers:
            pct = s.get("change_pct", 0)
            pct_str = f"{pct:+.2f}%" if isinstance(pct, (int, float)) else str(pct)
            lines.append(f"  {s.get('symbol', ''):<22} {pct_str}")
        lines.append("")

    # Top losers
    losers, error = get_top_losers(config.TOP_MOVERS_COUNT)
    if not error and losers:
        lines.append("<b>Top Losers:</b>")
        for s in losers:
            pct = s.get("change_pct", 0)
            pct_str = f"{pct:+.2f}%" if isinstance(pct, (int, float)) else str(pct)
            lines.append(f"  {s.get('symbol', ''):<22} {pct_str}")
        lines.append("")

    # Best and worst sector
    sectors, error = get_all_sectors()
    if not error and sectors:
        valid = [s for s in sectors if isinstance(s.get("change_pct"), (int, float))]
        if valid:
            best = max(valid, key=lambda x: x["change_pct"])
            worst = min(valid, key=lambda x: x["change_pct"])
            lines.append(f"Best Sector  : {best['name']}  {best['change_pct']:+.2f}%")
            lines.append(f"Worst Sector : {worst['name']}  {worst['change_pct']:+.2f}%")

    notifier_fn(token, chat_id, "\n".join(lines))
