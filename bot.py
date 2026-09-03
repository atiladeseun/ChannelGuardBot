import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, ADMIN_IDS
from database import init_db, add_user, get_user, add_channel, get_channels, log_join, get_today_joins
from handlers import start, add_channel_command, list_channels, help_command, daily_summary
import utils

logging.basicConfig(level=logging.INFO)

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addchannel", add_channel_command))
app.add_handler(CommandHandler("channels", list_channels))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("daily", daily_summary))

# Listen for new chat members (join events)
async def track_joins(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        for user_id in ADMIN_IDS:
            channels = get_channels(user_id)
            for ch in channels:
                if ch[2] == chat.id:  # channel_id
                    keyboard = [[InlineKeyboardButton("💬 Message", url=f"tg://user?id={member.id}")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    msg = (f"🚪 **New Member Joined**\n\n"
                           f"👤 {member.first_name}\n"
                           f"@{member.username or 'No username'}\n"
                           f"🆔 {member.id}")
                    await context.bot.send_message(chat_id=user_id, text=msg, reply_markup=reply_markup)
                    break

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_joins))

if __name__ == "__main__":
    init_db()
    print("🤖 ChannelGuard is running...")
    app.run_polling()
