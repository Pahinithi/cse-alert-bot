# CSE Stock Alert Bot

Automatic stock market alerts for the Colombo Stock Exchange (CSE).
Sends Telegram messages when stocks move significantly.
Runs automatically on GitHub every 30 minutes during market hours.
No server, no Mac, no coding knowledge needed. Completely free.

---

## What You Will Receive

### Automatic Alerts (no action needed from you)

Every 30 minutes from 9:30 AM to 2:30 PM, Monday to Friday:

- Daily market summary at 9:30 AM when market opens
- Any of the 289 CSE listed companies that gained more than 5% today
- Any of the 289 CSE listed companies that lost more than 5% today
- RSI below 30 for your watchlist stocks — oversold signal (possible buy opportunity)
- RSI above 70 for your watchlist stocks — overbought signal (possible sell signal)
- ASPI index moved more than 2% from previous day

> The bot monitors all 289 companies listed on the CSE for gain and loss alerts.
> You do not need to add every company manually — it checks all of them automatically.
> RSI alerts are limited to your personal WATCHLIST in config.py.

### Custom Alerts (you set via Telegram — no coding needed)

- `/alert LOLC.N0000 below 500` — notify when LOLC drops below Rs 500
- `/alert COMB.N0000 above 220` — notify when COMB rises above Rs 220
- Alert fires once then removes itself automatically

---

## What You Receive in Telegram — Full Examples

### No input needed — these arrive automatically

**1. Daily Summary (9:30 AM every market day)**
```
CSE MARKET OPEN - Daily Summary

ASPI     : 21,917
S&P SL20 : 6,090
Turnover : LKR 6.61B
Trades   : 42,272

Top Gainers:
  HAYL.R0000      +25.00%
  KPHL.N0000      +25.00%
  HVA.N0000       +24.64%

Top Losers:
  SEMB.X0000      -33.33%
  AAF.P0000       -13.21%

Best Sector  : Retailing     +10.96%
Worst Sector : Utilities     +2.37%
```

**2. Significant Gain Alert (any of 289 CSE companies)**
```
SIGNIFICANT GAIN

DIAL.N0000
Dialog Axiata PLC

Up +6.58% today
Current Price : Rs 32.40
Volume        : 18,436,256 shares
```

**3. Significant Loss Alert (any of 289 CSE companies)**
```
SIGNIFICANT LOSS

SEMB.X0000
SEYLAN BANK PLC

Down -33.33% today
Current Price : Rs 0.20
Volume        : 328,112 shares
```

**4. RSI Oversold Alert (watchlist stocks only)**
```
RSI OVERSOLD ALERT
Possible buy zone - RSI is very low

SAMP.N0000   RSI=28.4   Price=Rs 149.25
```

**5. RSI Overbought Alert (watchlist stocks only)**
```
RSI OVERBOUGHT ALERT
Possible sell zone - RSI is very high

COMB.N0000   RSI=74.2   Price=Rs 215.50
```

**6. ASPI Movement Alert**
```
ASPI UP ALERT

ASPI: 22,350
Change: +2.35%
Previous Close: 21,917
Market Turnover: LKR 6.61B
```

### You send these commands — bot replies at next scheduled run

**Send `/help` to your bot:**
```
CSE Alert Bot Commands

/alert SYMBOL below PRICE
  Send alert when price drops below target
  Example: /alert LOLC.N0000 below 500

/alert SYMBOL above PRICE
  Send alert when price rises above target
  Example: /alert COMB.N0000 above 220

/list
  Show all your active price alerts

/remove SYMBOL
  Remove alerts for a stock
  Example: /remove LOLC.N0000

/help
  Show this message
```

**Send `/alert LOLC.N0000 below 500`:**
```
Alert set

LOLC.N0000 below Rs 500.00
You will be notified when this condition is triggered.
Use /list to see all your active alerts.
```

**Send `/list`:**
```
Active Price Alerts:

  LOLC.N0000  below  Rs 500.00
  COMB.N0000  above  Rs 220.00
```

**When your custom alert triggers:**
```
PRICE ALERT TRIGGERED

LOLC.N0000
L O L C HOLDINGS PLC

Your target  : below Rs 500.00
Current price: Rs 498.50
Change today : -1.28%

This alert has been removed.
```

---

## Setup Guide — Step by Step (10 minutes, no coding)

### Step 1 — Create a Telegram Bot

1. Open Telegram on your phone or computer
2. Search for **BotFather** (blue tick, official bot)
3. Tap it and press **Start**
4. Send: `/newbot`
5. It asks for a name — type anything, example: `CSE Alert Bot`
6. It asks for a username — type anything ending in bot, example: `cse_myalerts_bot`
7. BotFather replies with a **token** that looks like: `7412365890:AAFxyz123...`
8. Copy and save this token — you will need it later

### Step 2 — Get Your Telegram Chat ID

1. In Telegram, search for **userinfobot**
2. Tap it and press **Start**
3. It replies with your ID number, example: `123456789`
4. Copy and save this number — you will need it later

### Step 3 — Start a Chat With Your New Bot

1. In Telegram, search for your bot username (the one you created in Step 1)
2. Press **Start**
3. This step is required — the bot cannot send you messages until you start a chat with it

### Step 4 — Create a GitHub Account

1. Go to [github.com](https://github.com)
2. Click **Sign up**
3. Create a free account
4. Verify your email

### Step 5 — Create a New Repository

1. After logging in, click the **+** button at the top right
2. Select **New repository**
3. Name it: `cse-alert-bot`
4. Set visibility to **Private**
5. Click **Create repository**

### Step 6 — Upload All Files

Upload these files to your repository by clicking **Add file > Upload files**:

```
main.py
alert_engine.py
custom_alerts.py
notifier.py
config.py
cse_api.py
tv_api.py
requirements.txt
custom_alerts.json
telegram_offset.json
```

For the workflow file, create it with the correct folder path:

1. Click **Add file > Create new file**
2. In the filename box type exactly this (including slashes):
   `.github/workflows/schedule.yml`
3. Paste the content of `schedule.yml`
4. Click **Commit new file**

### Step 7 — Add Your Telegram Token and Chat ID

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. On the left sidebar, click **Secrets and variables** then **Actions**
4. Click **New repository secret**

Add first secret:
```
Name:  TELEGRAM_TOKEN
Value: (paste the token from BotFather — Step 1)
```
Click **Add secret**

Add second secret:
```
Name:  TELEGRAM_CHAT_ID
Value: (paste your ID number from userinfobot — Step 2)
```
Click **Add secret**

### Step 8 — Enable GitHub Actions

1. Click the **Actions** tab at the top of your repository
2. If you see a message asking to enable workflows, click **Enable**
3. You should now see **CSE Stock Alert Bot** on the left side

### Step 9 — Run It Once to Activate

1. Click the **Actions** tab
2. Click **CSE Stock Alert Bot** on the left
3. Click **Run workflow** (right side)
4. Click the green **Run workflow** button to confirm
5. Wait about 1 minute
6. Check your Telegram — you should receive a message

After this one manual run, the bot will run automatically every 30 minutes during market hours. You never need to click anything again.

---

## No Input Required

The bot runs fully automatically. You do not need to send any messages or take any action during market hours. Alerts arrive in Telegram automatically whenever a condition is triggered.

The only time you send a message to the bot is when you want to set a custom price alert using the commands listed above.

---

## Customizing Alert Settings

Edit `config.py` in your GitHub repository to change thresholds:

```python
# Change 5.0 to 3.0 for more sensitive gain alerts
GAIN_ALERT_PCT = 5.0

# Change 5.0 to 3.0 for more sensitive loss alerts
LOSS_ALERT_PCT = 5.0

# Change 30 to 35 to get oversold alerts earlier
RSI_OVERSOLD = 30

# Change 70 to 65 to get overbought alerts earlier
RSI_OVERBOUGHT = 70

# Add or remove stocks for RSI monitoring
WATCHLIST = [
    "LOLC.N0000",
    "JKH.N0000",
    ...
]
```

After editing, click **Commit changes**. The next run will use your new settings automatically.

---

## Market Hours

```
Monday to Friday
9:30 AM to 2:30 PM Sri Lanka time (UTC+5:30)

Bot runs at:
9:30  10:00  10:30  11:00  11:30
12:00  12:30  1:00  1:30  2:00  2:30
```

---

## GitHub Actions Free Quota

```
GitHub gives 2,000 free minutes per month

This bot uses:
  11 runs per day x 1 minute each = 11 minutes/day
  11 x 22 trading days = 242 minutes/month

You use only 12% of your free quota.
Will never cost anything.
Resets on the 1st of every month.
```

---

## File Structure

```
cse-alert-bot/
  main.py                   Runs everything
  alert_engine.py           Checks market conditions and sends alerts
  custom_alerts.py          Handles your custom price alert commands
  notifier.py               Sends and reads Telegram messages
  config.py                 All your settings — edit this file only
  cse_api.py                Fetches live data from cse.lk
  tv_api.py                 Fetches RSI and indicators from TradingView
  requirements.txt          Python packages needed
  custom_alerts.json        Saves your active alerts (auto-managed)
  telegram_offset.json      Tracks Telegram messages (auto-managed)
  last_run.txt              Updated every run to keep GitHub active (auto-managed)
  .github/
    workflows/
      schedule.yml          Automatic schedule
```

---

## Data Sources

| Source | What it provides | Cost |
|---|---|---|
| cse.lk/api | Live prices, market summary, sectors, all 289 companies | Free |
| TradingView | RSI, MACD, Bollinger Bands, recommendations | Free |

---

## Cost

Everything is completely free:

- GitHub account: free
- GitHub Actions: 2,000 free minutes/month (this bot uses ~242)
- Telegram Bot API: free forever
- CSE API (cse.lk): free
- TradingView API: free

---

## Developer

Developed by **Nithilan Pahirathan**

For any questions or support, contact: nithilan32@gmail.com- tv_api.py              (copy from your cse-market-mcp-server repo)
- requirements.txt
- custom_alerts.json
- telegram_offset.json
- .github/workflows/schedule.yml

To upload: click Add file > Upload files in your GitHub repo.

For the .github/workflows/schedule.yml file you need to create the folder structure.
Easiest way: use GitHub's web editor — click Create new file, type the path as:
  .github/workflows/schedule.yml
Then paste the content.

### Step 6 — Add Telegram secrets to GitHub

1. Go to your repo on GitHub
2. Click Settings (top menu)
3. Click Secrets and variables > Actions (left menu)
4. Click New repository secret

Add these two secrets:

Name: TELEGRAM_TOKEN
Value: (paste the token from BotFather)

Name: TELEGRAM_CHAT_ID
Value: (paste your chat ID number)

### Step 7 — Enable GitHub Actions

1. Click the Actions tab in your repo
2. If prompted, click I understand my workflows, go ahead and enable them

### Step 8 — Test it manually

1. Go to Actions tab
2. Click CSE Stock Alert Bot on the left
3. Click Run workflow > Run workflow
4. Wait 1 minute
5. Check your Telegram — you should receive a message

---

## Customizing Alerts

Edit config.py to change alert thresholds:

- GAIN_ALERT_PCT = 5.0    Change to 3.0 for more sensitive gain alerts
- LOSS_ALERT_PCT = 5.0    Change to 3.0 for more sensitive loss alerts
- RSI_OVERSOLD = 30       Change to 35 to get earlier oversold signals
- RSI_OVERBOUGHT = 70     Change to 65 to get earlier overbought signals
- WATCHLIST               Add or remove stock symbols

Add stocks to WATCHLIST that you want monitored for RSI signals.

---

## Custom Price Alert Commands

Send these messages directly to your Telegram bot:

Set an alert:
  /alert LOLC.N0000 below 500
  /alert COMB.N0000 above 220
  /alert JKH.N0000 below 18

See all your alerts:
  /list

Remove an alert:
  /remove LOLC.N0000

Get help:
  /help

---

## File Structure

```
cse-alert-bot/
  main.py                   Entry point — runs everything
  alert_engine.py           Automatic alert checks
  custom_alerts.py          Custom price alert logic
  notifier.py               Sends Telegram messages
  config.py                 Your alert rules — edit this
  cse_api.py                CSE data layer (from MCP project)
  tv_api.py                 TradingView indicator layer (from MCP project)
  custom_alerts.json        Stores your custom alerts (auto-managed)
  telegram_offset.json      Tracks Telegram message position (auto-managed)
  requirements.txt          Python dependencies
  .github/
    workflows/
      schedule.yml          GitHub Actions schedule
```

---

## Cost

Everything is free:
- GitHub Actions: 2000 free minutes/month. This bot uses ~200 min/month.
- Telegram Bot API: free forever
- CSE API: free (unofficial)
- TradingView API: free (unofficial)
