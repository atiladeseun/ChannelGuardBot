import logging
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ===== CONFIGURATION - CHANGE THIS =====
BOT_TOKEN = "8355200203:AAFQfJTnMhJcn6b_Tvrgav1uMWhSi5LATpM"
ADMIN_IDS = [123456789]  # CHANGE THIS TO YOUR ID
# ======================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_PATH = "channelguard.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TEXT,
            trial_until TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            channel_id INTEGER,
            channel_title TEXT,
            added_at TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS joins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER,
            user_id INTEGER,
            username TEXT,
            first_name TEXT,
            joined_at TEXT
        )''')
        conn.commit()
        conn.close()
        logger.info("Database initialized")
        return True
    except Exception as e:
        logger.error(f"Database init error: {e}")
        return False

def add_user(user_id, username, first_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        trial_until = (datetime.now() + timedelta(days=4)).isoformat()
        c.execute("INSERT OR REPLACE INTO users (user_id, username, first_name, joined_at, trial_until) VALUES (?,?,?,?,?)",
                  (user_id, username or "", first_name or "", datetime.now().isoformat(), trial_until))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Add user error: {e}")

def add_channel(user_id, channel_id, channel_title):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO channels (user_id, channel_id, channel_title, added_at) VALUES (?,?,?,?)",
                  (user_id, channel_id, channel_title or "Unknown", datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Add channel error: {e}")

def get_channels(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM channels WHERE user_id = ?", (user_id,))
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Get channels error: {e}")
        return []

def log_join(channel_id, user_id, username, first_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO joins (channel_id, user_id, username, first_name, joined_at) VALUES (?,?,?,?,?)",
                  (channel_id, user_id, username or "", first_name or "", datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Log join error: {e}")

def get_today_joins(channel_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        today = datetime.now().date().isoformat()
        c.execute("SELECT * FROM joins WHERE channel_id = ? AND DATE(joined_at) = ?", (channel_id, today))
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Get today joins error: {e}")
        return []

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        add_user(user.id, user.username, user.first_name)
        
        text = (
            "🛡️ **ChannelGuard** – Instant join alerts for your Telegram channel.\n\n"
            "Get notified the moment someone joins. See their name, @username, "
            "and message them with one tap — before they forget why they subscribed.\n\n"
            "✅ Real-time join & leave alerts\n"
            "✅ One-tap reply to new members\n"
            "✅ Daily summary of all new joins\n"
            "✅ Monitor up to 3 channels\n\n"
            "🎁 **Free for 4 days.**\n"
            "💰 $30/month after – USDT or TON.\n\n"
            "Add me as admin to your channel and start protecting your community."
        )
        await update.message.reply_text(text, parse_mode="Markdown")
        logger.info(f"Start command from user {user.id}")
    except Exception as e:
        logger.error(f"Start error: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again.")

async def add_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        channels = get_channels(user_id)
        if len(channels) >= 3:
            await update.message.reply_text("❌ You've reached the max number of channels (3).")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /addchannel @channel_username")
            return
        
        channel_username = context.args[0]
        chat = await context.bot.get_chat(channel_username)
        add_channel(user_id, chat.id, chat.title)
        await update.message.reply_text(f"✅ Added channel: {chat.title}\nI'll now monitor it.")
    except Exception as e:
        logger.error(f"Add channel error: {e}")
        await update.message.reply_text(f"❌ Failed to add channel. Make sure I'm an admin.\nError: {str(e)}")

async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        channels = get_channels(user_id)
        if not channels:
            await update.message.reply_text("You haven't added any channels yet.")
            return
        text = "📋 **Your monitored channels:**\n"
        for ch in channels:
            text += f"- {ch[3]} (ID: {ch[2]})\n"
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"List channels error: {e}")
        await update.message.reply_text("❌ Error listing channels.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🆘 **Help**\n"
        "/start - Welcome & info\n"
        "/addchannel @channel - Add a channel to monitor\n"
        "/channels - List your monitored channels\n"
        "/daily - Get today's join summary\n"
        "/help - Show this message"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def daily_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        channels = get_channels(user_id)
        if not channels:
            await update.message.reply_text("No channels added.")
            return
        
        for ch in channels:
            joins = get_today_joins(ch[2])
            if joins:
                text = f"📊 **Daily Summary for {ch[3]}**\n\n"
                for j in joins:
                    text += f"👤 {j[4] or 'User'} (@{j[3] or 'no username'})\n"
            else:
                text = f"📊 No new joins for {ch[3]} today."
            await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Daily summary error: {e}")
        await update.message.reply_text("❌ Error getting summary.")

async def track_joins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.new_chat_members:
            return
        
        chat = update.effective_chat
        if chat.type not in ["channel", "supergroup"]:
            return
        
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                continue
            
            log_join(chat.id, member.id, member.username or "", member.first_name or "")
            
            for admin_id in ADMIN_IDS:
                channels = get_channels(admin_id)
                for ch in channels:
                    if ch[2] == chat.id:
                        keyboard = [[InlineKeyboardButton("💬 Message", url=f"tg://user?id={member.id}")]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        msg = (f"🚪 **New Member Joined**\n\n"
                               f"👤 {member.first_name or 'User'}\n"
                               f"@{member.username or 'No username'}\n"
                               f"🆔 {member.id}")
                        await context.bot.send_message(chat_id=admin_id, text=msg, reply_markup=reply_markup, parse_mode="Markdown")
                        break
    except Exception as e:
        logger.error(f"Track joins error: {e}")

def main():
    print("=" * 50)
    print("🤖 ChannelGuard Bot Starting...")
    print("=" * 50)
    
    # Initialize database
    if not init_db():
        print("❌ Failed to initialize database!")
        return
    
    # Verify token
    if not BOT_TOKEN or len(BOT_TOKEN) < 20:
        print("❌ Invalid BOT_TOKEN!")
        return
    
    print(f"✅ Token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
    print(f"✅ Admin IDs: {ADMIN_IDS}")
    
    try:
        # Create application
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("addchannel", add_channel_command))
        app.add_handler(CommandHandler("channels", list_channels))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("daily", daily_summary))
        app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_joins))
        
        print("✅ Bot is ready!")
        print("📡 Starting polling...")
        print("=" * 50)
        
        app.run_polling()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
