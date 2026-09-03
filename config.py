import os
from dotenv import load_dotenv
import sys

load_dotenv()

def validate_config():
    """Check if all required config values are set"""
    errors = []
    
    if not BOT_TOKEN:
        errors.append("BOT_TOKEN is missing in .env file")
    
    if not ADMIN_IDS or ADMIN_IDS == [0]:
        errors.append("ADMIN_IDS is missing or invalid in .env file")
    
    if errors:
        print("\n❌ Configuration errors:")
        for error in errors:
            print(f"   - {error}")
        print("\nPlease check your .env file and try again.\n")
        sys.exit(1)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = []
try:
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    if admin_ids_str:
        ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]
except ValueError:
    print("\n❌ ADMIN_IDS must be comma-separated numbers (e.g., 123456789,987654321)\n")
    sys.exit(1)

MAX_CHANNELS_PER_USER = 3
FREE_TRIAL_DAYS = 4
PRICE_USDT = 30
PRICE_TON = 30

# Validate configuration
validate_config()
