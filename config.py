# Stocks to monitor for RSI alerts (add or remove symbols as needed)
WATCHLIST = [
    "LOLC.N0000",
    "JKH.N0000",
    "COMB.N0000",
    "DIAL.N0000",
    "SAMP.N0000",
    "ABAN.N0000",
    "CARG.N0000",
    "HNB.N0000",
    "BUKI.N0000",
    "LION.N0000",
]

#  Automatic Alert Rules

# Send alert if any stock gains more than this % in one day
GAIN_ALERT_PCT = 5.0

# Send alert if any stock loses more than this % in one day
LOSS_ALERT_PCT = 5.0

# RSI below this = oversold (possible buy opportunity)
RSI_OVERSOLD = 30

# RSI above this = overbought (possible sell signal)
RSI_OVERBOUGHT = 70

# Send alert if ASPI index changes more than this % from previous day
ASPI_CHANGE_PCT = 2.0

# Daily Summary

# Send a market overview at 10:00 AM when market opens
SEND_DAILY_SUMMARY = True

# How many top gainers and losers to show in the daily summary
TOP_MOVERS_COUNT = 5

# Market Hours (Sri Lanka time)
MARKET_OPEN_HOUR = 10
MARKET_OPEN_MIN = 0
MARKET_CLOSE_HOUR = 14
MARKET_CLOSE_MIN = 30
