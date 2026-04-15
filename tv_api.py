import time
import json
import requests as _requests
from tradingview_ta import TA_Handler, Interval, get_multiple_analysis

EXCHANGE = "CSELK"
SCREENER = "srilanka"

INTERVAL_MAP = {
    "1m": Interval.INTERVAL_1_MINUTE,
    "5m": Interval.INTERVAL_5_MINUTES,
    "15m": Interval.INTERVAL_15_MINUTES,
    "30m": Interval.INTERVAL_30_MINUTES,
    "1h": Interval.INTERVAL_1_HOUR,
    "2h": Interval.INTERVAL_2_HOURS,
    "4h": Interval.INTERVAL_4_HOURS,
    "1d": Interval.INTERVAL_1_DAY,
    "1w": Interval.INTERVAL_1_WEEK,
    "1M": Interval.INTERVAL_1_MONTH,
}

DEFAULT_INTERVAL = "1d"

# Retry config
MAX_RETRIES = 4
BASE_DELAY = 3.0  # seconds — first retry wait
BACKOFF_MULT = 2.0  # each retry doubles the wait: 3s, 6s, 12s, 24s


def _resolve_interval(interval: str):
    key = interval if interval == "1M" else interval.lower()
    resolved = INTERVAL_MAP.get(key)
    if not resolved:
        return (
            None,
            f"Invalid interval '{interval}'. Valid: {list(INTERVAL_MAP.keys())}",
        )
    return resolved, None


def _retry(fn, *args, **kwargs):
    """
    Call fn(*args, **kwargs) with exponential backoff retry.
    Retries on:
      - Exception containing "429"
      - json.JSONDecodeError (empty body from TradingView)
      - ValueError "Expecting value" (same empty body)
    """
    delay = BASE_DELAY
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = fn(*args, **kwargs)
            return result, None
        except (json.JSONDecodeError, ValueError) as e:
            msg = str(e)
            if "Expecting value" in msg or "line 1 column 1" in msg:
                last_error = f"TradingView returned empty response (attempt {attempt}/{MAX_RETRIES})"
            else:
                return None, str(e)
        except Exception as e:
            msg = str(e)
            if "429" in msg or "rate" in msg.lower():
                last_error = f"Rate limited HTTP 429 (attempt {attempt}/{MAX_RETRIES})"
            else:
                return None, msg

        if attempt < MAX_RETRIES:
            time.sleep(delay)
            delay *= BACKOFF_MULT

    return (
        None,
        f"TradingView blocked after {MAX_RETRIES} retries. Last error: {last_error}. Wait 1-2 minutes and try again.",
    )


def get_indicators(symbol: str, interval: str = DEFAULT_INTERVAL) -> tuple:
    """
    Full technical analysis for one CSE symbol.
    Uses retry with exponential backoff.
    """
    tv_interval, error = _resolve_interval(interval)
    if error:
        return None, error

    def _fetch():
        handler = TA_Handler(
            symbol=symbol,
            screener=SCREENER,
            exchange=EXCHANGE,
            interval=tv_interval,
            timeout=15,
        )
        return handler.get_analysis()

    analysis, error = _retry(_fetch)
    if error:
        return None, error

    ind = analysis.indicators
    summary = analysis.summary
    osc = analysis.oscillators
    ma = analysis.moving_averages

    return {
        "symbol": symbol,
        "interval": interval,
        "summary": {
            "recommendation": summary.get("RECOMMENDATION"),
            "buy": summary.get("BUY"),
            "neutral": summary.get("NEUTRAL"),
            "sell": summary.get("SELL"),
        },
        "price": {
            "close": ind.get("close"),
            "open": ind.get("open"),
            "high": ind.get("high"),
            "low": ind.get("low"),
            "volume": ind.get("volume"),
        },
        "oscillators": {
            "rsi": ind.get("RSI"),
            "rsi_prev": ind.get("RSI[1]"),
            "macd": ind.get("MACD.macd"),
            "macd_signal": ind.get("MACD.signal"),
            "stoch_k": ind.get("Stoch.K"),
            "stoch_d": ind.get("Stoch.D"),
            "cci_20": ind.get("CCI20"),
            "adx": ind.get("ADX"),
            "mom": ind.get("Mom"),
            "ao": ind.get("AO"),
            "summary": {
                "recommendation": osc.get("RECOMMENDATION"),
                "buy": osc.get("BUY"),
                "neutral": osc.get("NEUTRAL"),
                "sell": osc.get("SELL"),
            },
        },
        "moving_averages": {
            "ema_10": ind.get("EMA10"),
            "ema_20": ind.get("EMA20"),
            "ema_50": ind.get("EMA50"),
            "ema_200": ind.get("EMA200"),
            "sma_10": ind.get("SMA10"),
            "sma_20": ind.get("SMA20"),
            "sma_50": ind.get("SMA50"),
            "sma_200": ind.get("SMA200"),
            "vwma": ind.get("VWMA"),
            "hull": ind.get("HullMA9"),
            "summary": {
                "recommendation": ma.get("RECOMMENDATION"),
                "buy": ma.get("BUY"),
                "neutral": ma.get("NEUTRAL"),
                "sell": ma.get("SELL"),
            },
        },
        "bollinger_bands": {
            "upper": ind.get("BB.upper"),
            "middle": ind.get("BB.middle"),
            "lower": ind.get("BB.lower"),
            "width": (
                round(ind.get("BB.upper", 0) - ind.get("BB.lower", 0), 4)
                if ind.get("BB.upper") and ind.get("BB.lower")
                else None
            ),
        },
    }, None


def get_bulk_indicators(symbols: list, interval: str = DEFAULT_INTERVAL) -> tuple:
    """
    Summary indicators for multiple symbols in ONE TradingView request.
    Use this instead of calling get_indicators() in a loop.
    Uses retry with exponential backoff.
    """
    tv_interval, error = _resolve_interval(interval)
    if error:
        return None, error

    tv_symbols = [f"{EXCHANGE}:{s}" for s in symbols]

    def _fetch():
        return get_multiple_analysis(
            screener=SCREENER,
            interval=tv_interval,
            symbols=tv_symbols,
            timeout=20,
        )

    raw, error = _retry(_fetch)
    if error:
        return None, error

    results = {}
    for key, analysis in raw.items():
        symbol = key.replace(f"{EXCHANGE}:", "")
        if analysis is None:
            results[symbol] = {"error": "No data returned"}
            continue
        ind = analysis.indicators
        summary = analysis.summary
        results[symbol] = {
            "recommendation": summary.get("RECOMMENDATION"),
            "buy": summary.get("BUY"),
            "neutral": summary.get("NEUTRAL"),
            "sell": summary.get("SELL"),
            "rsi": ind.get("RSI"),
            "macd": ind.get("MACD.macd"),
            "macd_signal": ind.get("MACD.signal"),
            "close": ind.get("close"),
            "volume": ind.get("volume"),
            "bb_upper": ind.get("BB.upper"),
            "bb_lower": ind.get("BB.lower"),
            "ema_20": ind.get("EMA20"),
            "sma_50": ind.get("SMA50"),
        }
    return results, None


def screen_by_recommendation(
    symbols: list,
    recommendation: str,
    interval: str = DEFAULT_INTERVAL,
) -> tuple:
    bulk, error = get_bulk_indicators(symbols, interval)
    if error:
        return None, error
    target = recommendation.upper()
    return {
        sym: data
        for sym, data in bulk.items()
        if data.get("recommendation", "").upper() == target
    }, None


def screen_by_rsi(
    symbols: list,
    min_rsi: float = 0,
    max_rsi: float = 100,
    interval: str = DEFAULT_INTERVAL,
) -> tuple:
    bulk, error = get_bulk_indicators(symbols, interval)
    if error:
        return None, error
    return {
        sym: data
        for sym, data in bulk.items()
        if isinstance(data.get("rsi"), float) and min_rsi <= data["rsi"] <= max_rsi
    }, None
