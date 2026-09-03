import logging
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, ADMIN_IDS
from database import init_db, add_user, get_user, add_channel, get_channels, log_join, get_today_joins
from handlers import start, add_channel_command, list_channels, help_command, daily_summary

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global app variable
app = None

async def track_joins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.new_chat_members:
            return

        chat = update.effective_chat
        if chat.type not in ["channel", "supergroup"]:
            return

        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                continue  # bot itself joining

            # Log join
            log_join(chat.id, member.id, member.username or "", member.first_name or "")

            # Notify channel admins who use this bot
            for admin_id in ADMIN_IDS:
                channels = get_channels(admin_id)
                for ch in channels:
                    if ch[2] == chat.id:  # channel_id
                        keyboard = [[InlineKeyboardButton("💬 Message", url=f"tg://user?id={member.id}")]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        msg = (f"🚪 **New Member Joined**\n\n"
                               f"👤 {member.first_name or 'User'}\n"
                               f"@{member.username or 'No username'}\n"
                               f"🆔 {member.id}")
                        try:
                            await context.bot.send_message(
                                chat_id=admin_id, 
                                text=msg, 
                                reply_markup=reply_markup,
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            logger.error(f"Failed to send message to admin {admin_id}: {e}")
                        break

    except Exception as e:
        logger.error(f"Error in track_joins: {e}")

def main():
    global app
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        
        # Create application
        logger.info("Creating bot application...")
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("addchannel", add_channel_command))
        app.add_handler(CommandHandler("channels", list_channels))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("daily", daily_summary))
        app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_joins))
        
        # Start bot
        logger.info("🤖 ChannelGuard is starting...")
        print("\n✅ ChannelGuard is running! Press Ctrl+C to stop.\n")
        
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
