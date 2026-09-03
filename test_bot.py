import os
import sys
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("=" * 50)
print("🔍 DEBUGGING CHANNELGUARD")
print("=" * 50)

# Step 1: Check .env file
print("\n1️⃣ Checking .env file...")
env_path = ".env"
if os.path.exists(env_path):
    print(f"✅ .env file found at: {os.path.abspath(env_path)}")
    with open(env_path, 'r') as f:
        content = f.read()
        print("📄 .env content (hidden token):")
        for line in content.split('\n'):
            if line.startswith('BOT_TOKEN='):
                token = line.replace('BOT_TOKEN=', '').strip()
                if len(token) > 10:
                    print(f"   BOT_TOKEN={token[:10]}...{token[-5:]}")
                else:
                    print(f"   BOT_TOKEN={token}")
            elif line.startswith('ADMIN_IDS='):
                print(f"   {line}")
            elif line.strip():
                print(f"   {line}")
else:
    print(f"❌ .env file NOT found at: {os.path.abspath(env_path)}")
    sys.exit(1)

# Step 2: Check variables
print("\n2️⃣ Loading environment variables...")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_IDS")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN is empty or not set")
    sys.exit(1)
else:
    print(f"✅ BOT_TOKEN loaded: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")

if not ADMIN_IDS:
    print("❌ ADMIN_IDS is empty or not set")
    sys.exit(1)
else:
    print(f"✅ ADMIN_IDS loaded: {ADMIN_IDS}")

# Step 3: Test Telegram API
print("\n3️⃣ Testing Telegram API...")
import requests
try:
    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            print(f"✅ Bot connection successful!")
            print(f"   Bot Name: {data['result']['first_name']}")
            print(f"   Bot Username: @{data['result']['username']}")
        else:
            print(f"❌ API returned error: {data}")
            sys.exit(1)
    else:
        print(f"❌ HTTP error: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Connection error: {e}")
    sys.exit(1)

# Step 4: Test database
print("\n4️⃣ Testing database...")
try:
    import sqlite3
    conn = sqlite3.connect("test.db")
    conn.execute("CREATE TABLE test (id INTEGER)")
    conn.execute("INSERT INTO test VALUES (1)")
    conn.commit()
    result = conn.execute("SELECT * FROM test").fetchone()
    conn.close()
    import os
    os.remove("test.db")
    print("✅ Database working")
except Exception as e:
    print(f"❌ Database error: {e}")
    sys.exit(1)

# Step 5: Try importing telegram
print("\n5️⃣ Testing telegram library...")
try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder
    print("✅ Telegram library imported successfully")
    print(f"   Version: {__import__('telegram').__version__}")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Run: pip install python-telegram-bot==20.7")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("✅ ALL TESTS PASSED! Your bot should work.")
print("=" * 50)
print("\nNow run: python bot.py")
