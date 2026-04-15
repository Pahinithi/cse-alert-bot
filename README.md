# CSE Stock Alert Bot

Automatic stock alerts for the Colombo Stock Exchange.
Sends Telegram messages when stocks move significantly.
Runs automatically on GitHub — no server or Mac needed.
Completely free.

---

## What You Will Receive

Automatic alerts every 30 minutes during market hours (10:00 AM - 2:30 PM):

- Stock gained more than 5% today
- Stock lost more than 5% today
- RSI below 30 (oversold signal)
- RSI above 70 (overbought signal)
- ASPI index moved more than 2%
- Daily market summary at 10:00 AM

Custom alerts you set yourself:

- /alert LOLC.N0000 below 500  (alert when LOLC drops below Rs 500)
- /alert COMB.N0000 above 220  (alert when COMB rises above Rs 220)

---

## Setup Guide (10 minutes, no coding)

### Step 1 — Create a Telegram Bot

1. Open Telegram on your phone
2. Search for: BotFather
3. Send: /newbot
4. Choose a name: CSE Alert Bot
5. Choose a username: cse_alert_yourname_bot
6. BotFather gives you a token like: 7412365890:AAFxyz123...
7. Copy and save this token

### Step 2 — Get your Telegram Chat ID

1. Search for: userinfobot  in Telegram
2. Send: /start
3. It replies with your ID number like: 123456789
4. Copy and save this number

### Step 3 — Create a GitHub account

Go to github.com and create a free account if you do not have one.

### Step 4 — Create a new GitHub repository

1. Click the + button at the top right of GitHub
2. Select New repository
3. Name it: cse-alert-bot
4. Set it to Private
5. Click Create repository

### Step 5 — Upload files to GitHub

Upload all these files to your new repository:

- main.py
- alert_engine.py
- custom_alerts.py
- notifier.py
- config.py
- cse_api.py             (copy from your cse-market-mcp-server repo)
- tv_api.py              (copy from your cse-market-mcp-server repo)
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
