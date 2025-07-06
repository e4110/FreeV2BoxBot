import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

TOKEN = "7336765866:AAEVhmNyhP3TVml9psl_WJ4r9FneZPiNb9E"
ADMIN_ID = 1511064812
CHANNEL_USERNAME = "@LiveTetherPrice"
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("config", "")
    except:
        return ""

def save_config(text):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"config": text}, f)

async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if await is_user_in_channel(context, user_id):
        buttons = [
            [InlineKeyboardButton("📥 دریافت کانفیگ", callback_data="get_config")],
            [InlineKeyboardButton("✉️ ارتباط با ادمین", callback_data="contact_admin")]
        ]
        await update.message.reply_text("به ربات خوش اومدی. یکی از گزینه‌ها رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await update.message.reply_text(f"برای استفاده از ربات ابتدا عضو کانال {CHANNEL_USERNAME} شوید و سپس /start را بزنید.")

async def is_user_in_channel(context, user_id):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "get_config":
        if await is_user_in_channel(context, user_id):
            config = load_config()
            if config:
                await query.message.reply_text(f"📦 کانفیگ فعلی:\n\n{config}")
            else:
                await query.message.reply_text("❌ هنوز هیچ کانفیگی ثبت نشده.")
        else:
            await query.message.reply_text(f"ابتدا عضو کانال {CHANNEL_USERNAME} شوید.")

    elif query.data == "contact_admin":
        await query.message.reply_text("پیامت رو بفرست تا به ادمین فوروارد بشه.")

async def forward_to_admin(update: Update, context: CallbackContext):
    if update.message.text:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📩 پیام از کاربر: {update.effective_user.full_name} 👤 ID: {update.effective_user.id}\n\n{update.message.text}")
        await update.message.reply_text("✅ پیامت ارسال شد. منتظر پاسخ باش.")

async def admin_reply(update: Update, context: CallbackContext):
    if update.message.reply_to_message and "ID:" in update.message.reply_to_message.text:
        lines = update.message.reply_to_message.text.split("ID:")
        if len(lines) > 1:
            target_id = int(lines[1].split()[0])
            await context.bot.send_message(chat_id=target_id, text=f"📨 پاسخ ادمین:\n\n{update.message.text}")
    elif update.message.text.startswith("/add "):
        save_config(update.message.text[5:])
        await update.message.reply_text("✅ کانفیگ ذخیره شد.")
    elif update.message.text == "/get":
        await update.message.reply_text(f"📦 آخرین کانفیگ:\n\n{load_config()}")
    elif update.message.text == "/delete":
        save_config("")
        await update.message.reply_text("🗑️ کانفیگ حذف شد.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(ADMIN_ID), admin_reply))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.User(ADMIN_ID)), forward_to_admin))
    app.run_polling()

if __name__ == "__main__":
    main()