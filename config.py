import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
MAX_CHANNELS_PER_USER = 3
FREE_TRIAL_DAYS = 4
PRICE_USDT = 30
PRICE_TON = 30  # in TON
