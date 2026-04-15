import requests
from datetime import datetime

BASE_URL = "https://www.cse.lk/api/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
TIMEOUT = 15

PERIOD_MAP = {
    "1D": 0,
    "1W": 0,
    "1M": 1,
    "3M": 3,
    "6M": 6,
    "1Y": 12,
}


def _post(endpoint: str, payload: dict = None) -> tuple:
    try:
        response = requests.post(
            BASE_URL + endpoint,
            data=payload or {},
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.Timeout:
        return None, f"Request timed out after {TIMEOUT}s"
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to cse.lk"
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP {response.status_code}: {str(e)}"
    except Exception as e:
        return None, str(e)


def get_company_info(symbol: str) -> tuple:
    data, error = _post("companyInfoSummery", {"symbol": symbol})
    if error:
        return None, error
    try:
        info = data.get("reqSymbolInfo", {})
        beta = data.get("reqSymbolBetaInfo", {})
        logo = data.get("reqLogo", {})
        return {
            "symbol": info.get("symbol"),
            "name": info.get("name"),
            "last_traded_price": info.get("lastTradedPrice"),
            "change": info.get("change"),
            "change_pct": info.get("changePercentage"),
            "market_cap": info.get("marketCap"),
            "stock_id": logo.get("id"),
            "beta_spsl": beta.get("betaValueSPSL"),
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }, None
    except Exception as e:
        return None, f"Parse error: {e}"


def get_market_summary() -> tuple:
    """
    dailyMarketSummery returns a list of daily market stat objects.
    Each item in the list can be:
      - a dict directly
      - a list wrapping one dict: [{...}]
    This handles both cases.
    """
    data, error = _post("dailyMarketSummery")
    if error:
        return None, error

    try:
        raw_list = data if isinstance(data, list) else []
        if not raw_list:
            return (
                None,
                f"Empty response. Raw type: {type(data)}, value: {str(data)[:200]}",
            )

        results = []
        for item in raw_list:
            # Unwrap single-element list: [{...}] -> {...}
            if isinstance(item, list):
                if len(item) == 0:
                    continue
                item = item[0]

            if not isinstance(item, dict):
                continue

            results.append(
                {
                    "trade_date": item.get("tradeDate"),
                    "asi": item.get("asi"),
                    "sp_sl20": item.get("spp"),
                    "triasi": item.get("triasi"),
                    "market_turnover": item.get("marketTurnover"),
                    "equity_turnover": item.get("equityTurnover"),
                    "market_trades": item.get("tradesNo"),
                    "domestic_trades": item.get("tradesNoDomestic"),
                    "foreign_trades": item.get("tradesNoForeign"),
                    "volume": item.get("volumeOfTurnOverNumber"),
                    "market_cap": item.get("marketCap"),
                    "listed_companies": item.get("listedCompanyNumber"),
                    "traded_companies": item.get("tradeCompanyNumber"),
                    "per": item.get("per"),
                    "pbv": item.get("pbv"),
                    "dividend_yield": item.get("dy"),
                    "domestic_purchase": item.get("equityDomesticPurchase"),
                    "domestic_sales": item.get("equityDomesticSales"),
                    "foreign_purchase": item.get("equityForeignPurchase"),
                    "foreign_sales": item.get("equityForeignSales"),
                }
            )

        return results, None
    except Exception as e:
        return None, f"Parse error: {e} — raw: {str(data)[:300]}"


def get_all_sectors() -> tuple:
    data, error = _post("allSectors")
    if error:
        return None, error
    try:
        sectors_raw = data if isinstance(data, list) else []
        results = []
        for s in sectors_raw:
            if not isinstance(s, dict):
                continue
            results.append(
                {
                    "sector_id": s.get("sectorId"),
                    "symbol": s.get("symbol"),
                    "name": s.get("name"),
                    "index_name": s.get("indexName"),
                    "index_value": s.get("indexValue"),
                    "change": s.get("change"),
                    "change_pct": s.get("percentage"),
                    "trades_today": s.get("sectorTradeToday"),
                    "volume_today": s.get("sectorVolumeToday"),
                    "turnover_today": s.get("sectorTurnoverToday"),
                    "previous_close": s.get("sectorPreviousClose"),
                }
            )
        return results, None
    except Exception as e:
        return None, f"Parse error: {e}"


def get_chart_data(symbol: str, period: str = "1M") -> tuple:
    """
    Fetches OHLCV chart data using numeric stockId and numeric period.
    period: "1D", "1W", "1M", "3M", "6M", "1Y"
    """
    company, error = get_company_info(symbol)
    if error:
        return None, f"Cannot get stockId for {symbol}: {error}"

    stock_id = company.get("stock_id")
    if not stock_id:
        return None, f"No stockId found for {symbol}"

    numeric_period = PERIOD_MAP.get(period.upper())
    if numeric_period is None:
        return None, f"Invalid period '{period}'. Valid: {list(PERIOD_MAP.keys())}"

    data, error = _post(
        "companyChartDataByStock",
        {
            "stockId": stock_id,
            "period": numeric_period,
        },
    )
    if error:
        return None, error

    try:
        # Debug: show raw response structure for first call
        raw_debug = {
            "response_type": str(type(data)),
            "keys_if_dict": list(data.keys()) if isinstance(data, dict) else "N/A",
            "length_if_list": len(data) if isinstance(data, list) else "N/A",
            "sample": str(data)[:500],
        }

        candles_raw = None
        if isinstance(data, list):
            candles_raw = data
        elif isinstance(data, dict):
            for key, val in data.items():
                if isinstance(val, list):
                    candles_raw = val
                    break

        if candles_raw is None:
            return {
                "symbol": symbol,
                "stock_id": stock_id,
                "period": period,
                "count": 0,
                "candles": [],
                "raw_debug": raw_debug,
                "note": "No list found in response — check raw_debug for correct field name",
            }, None

        if len(candles_raw) == 0:
            return {
                "symbol": symbol,
                "stock_id": stock_id,
                "period": period,
                "count": 0,
                "candles": [],
                "raw_debug": raw_debug,
                "note": "Empty list returned. Either outside market hours or period param is wrong.",
            }, None

        candles = []
        for c in candles_raw:
            if isinstance(c, list):
                candles.append(
                    {
                        "timestamp": c[0] if len(c) > 0 else None,
                        "open": c[1] if len(c) > 1 else None,
                        "high": c[2] if len(c) > 2 else None,
                        "low": c[3] if len(c) > 3 else None,
                        "close": c[4] if len(c) > 4 else None,
                        "volume": c[5] if len(c) > 5 else None,
                    }
                )
            elif isinstance(c, dict):
                candles.append(
                    {
                        "timestamp": c.get("date")
                        or c.get("time")
                        or c.get("timestamp"),
                        "open": c.get("open"),
                        "high": c.get("high"),
                        "low": c.get("low"),
                        "close": c.get("close"),
                        "volume": c.get("volume"),
                    }
                )

        return {
            "symbol": symbol,
            "stock_id": stock_id,
            "period": period,
            "count": len(candles),
            "candles": candles,
        }, None

    except Exception as e:
        return None, f"Parse error: {e}"


def get_detailed_trades() -> tuple:
    data, error = _post("detailedTrades")
    if error:
        return None, error
    try:
        trades_raw = data.get("reqDetailTrades", []) if isinstance(data, dict) else []
        return [
            {
                "symbol": t.get("symbol"),
                "name": t.get("name"),
                "price": t.get("price"),
                "change": t.get("change"),
                "change_pct": t.get("changePercentage") or t.get("changePct"),
                "qty": t.get("qty"),
                "trades": t.get("trades"),
                "turnover": t.get("turnover"),
                "volume": t.get("volume"),
            }
            for t in trades_raw
        ], None
    except Exception as e:
        return None, f"Parse error: {e}"


def _dedupe(trades: list) -> list:
    seen, unique = set(), []
    for t in trades:
        sym = t.get("symbol")
        if sym and sym not in seen:
            seen.add(sym)
            unique.append(t)
    return unique


def get_top_gainers(limit: int = 10) -> tuple:
    trades, error = get_detailed_trades()
    if error:
        return None, error
    filtered = sorted(
        [t for t in trades if isinstance(t.get("change_pct"), (int, float))],
        key=lambda x: x["change_pct"],
        reverse=True,
    )
    return _dedupe(filtered)[:limit], None


def get_top_losers(limit: int = 10) -> tuple:
    trades, error = get_detailed_trades()
    if error:
        return None, error
    filtered = sorted(
        [t for t in trades if isinstance(t.get("change_pct"), (int, float))],
        key=lambda x: x["change_pct"],
    )
    return _dedupe(filtered)[:limit], None


def get_top_volume(limit: int = 10) -> tuple:
    trades, error = get_detailed_trades()
    if error:
        return None, error
    filtered = sorted(
        [t for t in trades if isinstance(t.get("qty"), (int, float))],
        key=lambda x: x["qty"],
        reverse=True,
    )
    return _dedupe(filtered)[:limit], None
