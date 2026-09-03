# ChannelGuard

**ChannelGuard** is a Telegram bot that monitors your channels and sends instant alerts when new members join. It helps you engage with subscribers before they forget why they joined.

## Features
- Instant join alerts with name, username, and message button
- Daily summary of new members
- Supports up to 3 channels per user
- Free 4-day trial, then $30/month (USDT or TON)

## Setup
1. Clone this repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with `BOT_TOKEN` and `ADMIN_IDS`
4. Run: `python bot.py`

## Commands
- `/start` – Show info
- `/addchannel @channel` – Add a channel
- `/channels` – List monitored channels
- `/daily` – Today's join summary
- `/help` – Help message
