from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import add_user, get_user, add_channel, get_channels, get_today_joins
from config import FREE_TRIAL_DAYS, PRICE_USDT, PRICE_TON, MAX_CHANNELS_PER_USER
import utils
from datetime import datetime

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)

    text = (
        "🛡️ **Welcome to ChannelGuard**\n\n"
        "I monitor your channel and alert you instantly when someone joins.\n\n"
        "✅ Instant join & leave alerts\n"
        "✅ One-tap message new subscribers\n"
        "✅ Daily join summary\n"
        f"✅ Up to {MAX_CHANNELS_PER_USER} channels\n\n"
        f"🎁 **Free trial**: {FREE_TRIAL_DAYS} days\n"
        f"💰 After trial: ${PRICE_USDT} USDT or {PRICE_TON} TON / month\n\n"
        "To start, add me as an admin to your channel, then use /addchannel"
    )
    await update.message.reply_text(text)

async def add_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    channels = get_channels(user_id)
    if len(channels) >= MAX_CHANNELS_PER_USER:
        await update.message.reply_text("❌ You've reached the max number of channels.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /addchannel @channel_username")
        return

    channel_username = context.args[0]
    try:
        chat = await context.bot.get_chat(channel_username)
        add_channel(user_id, chat.id, chat.title)
        await update.message.reply_text(f"✅ Added channel: {chat.title}\nI'll now monitor it.")
    except Exception as e:
        await update.message.reply_text("❌ Failed to add channel. Make sure I'm an admin and the username is correct.")

async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    channels = get_channels(user_id)
    if not channels:
        await update.message.reply_text("You haven't added any channels yet.")
        return
    text = "📋 **Your monitored channels:**\n"
    for ch in channels:
        text += f"- {ch[3]} (ID: {ch[2]})\n"
    await update.message.reply_text(text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🆘 **Help**\n"
        "/start - Welcome & info\n"
        "/addchannel @channel - Add a channel to monitor\n"
        "/channels - List your monitored channels\n"
        "/daily - Get today's join summary\n"
        "/help - Show this message"
    )
    await update.message.reply_text(text)

async def daily_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                text += f"👤 {j[4] or 'User'} (@{j[3] or 'no username'}) at {j[5][:10]}\n"
        else:
            text = f"📊 No new joins for {ch[3]} today."
        await update.message.reply_text(text)
