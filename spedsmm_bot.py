"""
SpedSMMBot - боти SMM-панель (Накрутка) барои Telegram

ТАРЗИ КОР:
1. pip install python-telegram-bot
2. Токени аз @BotFather-ро дар поён гузоред
3. python spedsmm_bot.py

ЭЗОҲ: Ин скелети пурра аст бо тамоми менюҳо кор мекунад,
вале барои НАКРУТКАИ ВОҚЕӢ (лайк/обуна фиристодан) ва
ПАРДОХТИ ВОҚЕӢ (карт/E-money) шумо бояд:
  - API-и провайдери SMM (масалан smmpanel.com, JAP ва мон.) пайваст кунед
  - API-и системаи пардохт (Payme, Click, ё карти бонкӣ) пайваст кунед
Ҷойҳое ки бояд пур карда шаванд бо "# TODO" ишора шудаанд.
"""

import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# ===== ТОКЕНИ БОТРО ИНҶО ГУЗОРЕД =====
TOKEN = "8513803588:AAFuGXZM3rNf_hk_LfAVAe5VsC8fKSMRlec"
# =======================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_FILE = "users_db.json"

# ---------- "Пойгоҳи додаҳо" — файли JSON (барои оғоз соддагӣ) ----------
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_user(db, user_id):
    uid = str(user_id)
    if uid not in db:
        db[uid] = {"balance": 0.0, "orders": [], "referrals": 0, "referred_by": None}
    return db[uid]


# ---------- Менюи асосӣ ----------
MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["💎 Накрутка задан", "📱 Гирифтани рақам"],
        ["⭐ Premium / Stars", "🎮 Донат ба бозиҳо"],
        ["💳 Ҳисоби ман", "💰 Пур кардани ҳисоб"],
        ["👥 Реферал", "🛒 Фармоишҳо"],
        ["📚 Маълумотҳо", "🤝 Ҳамкорӣ"],
    ],
    resize_keyboard=True
)

# ---------- Хизматҳои накрутка (намуна — нархҳоро худ иваз кунед) ----------
SERVICES = {
    "like_instagram": {"name": "Лайк Instagram", "price_per_1000": 5.0},
    "views_instagram": {"name": "Вьюс Instagram", "price_per_1000": 2.0},
    "followers_instagram": {"name": "Обуначиён Instagram", "price_per_1000": 15.0},
    "views_tiktok": {"name": "Вьюс TikTok", "price_per_1000": 1.5},
    "likes_tiktok": {"name": "Лайк TikTok", "price_per_1000": 4.0},
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    user = get_user(db, update.effective_user.id)

    # Коркарди реферал (агар бо линк омада бошад: /start REFID)
    if context.args:
        ref_id = context.args[0]
        if ref_id != str(update.effective_user.id) and user["referred_by"] is None:
            user["referred_by"] = ref_id
            ref_user = get_user(db, ref_id)
            ref_user["referrals"] += 1
            ref_user["balance"] += 0.5  # мукофоти реферал
    save_db(db)

    await update.message.reply_text(
        f"Хуш омадед ба SpedSMM Bot! 🎉\n\n"
        f"Дар ин бот шумо метавонед:\n"
        f"• Накрутка (лайк, обуна, вьюс) фармоиш диҳед\n"
        f"• Рақами телефон гиред\n"
        f"• Premium/Stars харед\n"
        f"• Ба бозиҳо донат кунед\n\n"
        f"Аз менюи поён интихоб кунед 👇",
        reply_markup=MAIN_MENU
    )


async def my_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    user = get_user(db, update.effective_user.id)
    save_db(db)
    await update.message.reply_text(
        f"💳 Ҳисоби шумо\n\n"
        f"🆔 ID: {update.effective_user.id}\n"
        f"💰 Балансатон: {user['balance']:.2f} сомонӣ\n"
        f"🛒 Шумораи фармоишҳо: {len(user['orders'])}\n"
        f"👥 Рефералҳо: {user['referrals']}"
    )


async def top_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Ин ҷо линки пардохти воқеиро (Payme/Click/карт) пайваст кунед
    await update.message.reply_text(
        "💰 Пур кардани ҳисоб\n\n"
        "Роҳҳои пардохт:\n"
        "• Карти бонкӣ: 0000 0000 0000 0000 (номи қабулкунанда)\n"
        "• Баъд аз пардохт, чек/скриншотро ба админ фиристед: @ALIJON\n\n"
        "⚠️ Баъд аз тасдиқ, маблағ ба ҳисоби шумо гузошта мешавад."
    )
    # TODO: Дар ҷои воқеӣ, ин бояд бо системаи пардохти автоматӣ (webhook) иваз шавад


async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_username = (await context.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={update.effective_user.id}"
    await update.message.reply_text(
        f"👥 Барномаи реферал\n\n"
        f"Барои ҳар як дӯсте ки бо линки шумо ба бот ҳамроҳ шавад, "
        f"шумо 0.5 сомонӣ мегиред!\n\n"
        f"🔗 Линки шумо:\n{link}"
    )


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    user = get_user(db, update.effective_user.id)
    save_db(db)
    if not user["orders"]:
        await update.message.reply_text("Шумо ҳанӯз фармоише надоред.")
        return
    text = "🛒 Фармоишҳои шумо:\n\n"
    for i, order in enumerate(user["orders"], 1):
        text += f"{i}. {order['service']} — {order['quantity']} дона — {order['price']:.2f} сомонӣ\n"
    await update.message.reply_text(text)


async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"{s['name']} — {s['price_per_1000']} сом/1000", callback_data=key)]
        for key, s in SERVICES.items()
    ]
    await update.message.reply_text(
        "💎 Хизматҳои мавҷуда — интихоб кунед:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def service_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    service_key = query.data
    service = SERVICES.get(service_key)
    if not service:
        return
    context.user_data["pending_service"] = service_key
    await query.message.reply_text(
        f"Шумо интихоб кардед: {service['name']}\n"
        f"Нарх: {service['price_per_1000']} сомонӣ барои 1000 дона\n\n"
        f"Линки видео/акаунтро фиристед ва миқдорро нишон диҳед.\n"
        f"Масалан: https://instagram.com/p/xxxxx 1000"
    )


async def handle_order_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Агар корбар пас аз интихоби хизмат линк+миқдор фиристад."""
    pending = context.user_data.get("pending_service")
    if not pending:
        return
    parts = update.message.text.rsplit(" ", 1)
    if len(parts) != 2 or not parts[1].isdigit():
        await update.message.reply_text("Формат нодуруст. Мисол: https://link.com 1000")
        return

    link, qty = parts[0], int(parts[1])
    service = SERVICES[pending]
    price = round(service["price_per_1000"] * qty / 1000, 2)

    db = load_db()
    user = get_user(db, update.effective_user.id)

    if user["balance"] < price:
        await update.message.reply_text(
            f"❌ Балансатон кофӣ нест. Нарх: {price} сомонӣ, дар ҳисоб: {user['balance']:.2f} сомонӣ.\n"
            f"Аввал ҳисобро пур кунед: 💰 Пур кардани ҳисоб"
        )
        return

    # TODO: Дар ин ҷо API-и провайдери SMM-ро даъват кунед (масалан JAP, SMMpanel):
    # response = requests.post("https://provider.com/api/v2", data={...})

    user["balance"] -= price
    user["orders"].append({"service": service["name"], "quantity": qty, "link": link, "price": price})
    save_db(db)
    context.user_data["pending_service"] = None

    await update.message.reply_text(
        f"✅ Фармоиш қабул шуд!\n\n"
        f"📦 Хизмат: {service['name']}\n"
        f"🔗 Ҳавола: {link}\n"
        f"🔢 Миқдор: {qty}\n"
        f"💵 Нарх: {price} сомонӣ\n\n"
        f"🙏 Ташаккур барои фармоишатон!"
    )


async def get_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Пайваст кардан ба сервиси рақами виртуалӣ (масалан SMS-activate)
    await update.message.reply_text(
        "📱 Гирифтани рақами виртуалӣ\n\n"
        "Ин хизмат ҳоло дар ҳоли омодасозист. Барои маълумот ба @ALIJON муроҷиат кунед."
    )


async def premium_stars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⭐ Premium / Telegram Stars\n\n"
        "• Telegram Premium (1 моҳ) — 45 сомонӣ\n"
        "• 100 Stars — 12 сомонӣ\n"
        "• 500 Stars — 55 сомонӣ\n\n"
        "Барои фармоиш, ба админ нависед: @ALIJON"
    )


async def game_donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Донат ба бозиҳо\n\n"
        "PUBG UC, Free Fire Diamonds, Mobile Legends ва диг.\n"
        "Барои фармоиш, ба админ нависед: @ALIJON"
    )


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Маълумот дар бораи бот\n\n"
        "SpedSMM Bot — хизмати накрутка ва хизматҳои рақамӣ.\n"
        "Дастгирӣ: @ALIJON"
    )


async def cooperation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤝 Ҳамкорӣ\n\n"
        "Агар мехоҳед бо мо ҳамкорӣ кунед (реселлер, реклама ва ғ.), "
        "ба админ нависед: @ALIJON"
    )


def main():
    if TOKEN == "YOUR_TOKEN_HERE":
        print("ХАТО: Аввал токенро дар боло гузоред!")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^💎 Накрутка задан$"), show_services))
    app.add_handler(MessageHandler(filters.Regex("^📱 Гирифтани рақам$"), get_number))
    app.add_handler(MessageHandler(filters.Regex("^⭐ Premium / Stars$"), premium_stars))
    app.add_handler(MessageHandler(filters.Regex("^🎮 Донат ба бозиҳо$"), game_donate))
    app.add_handler(MessageHandler(filters.Regex("^💳 Ҳисоби ман$"), my_account))
    app.add_handler(MessageHandler(filters.Regex("^💰 Пур кардани ҳисоб$"), top_up))
    app.add_handler(MessageHandler(filters.Regex("^👥 Реферал$"), referral))
    app.add_handler(MessageHandler(filters.Regex("^🛒 Фармоишҳо$"), my_orders))
    app.add_handler(MessageHandler(filters.Regex("^📚 Маълумотҳо$"), info))
    app.add_handler(MessageHandler(filters.Regex("^🤝 Ҳамкорӣ$"), cooperation))

    app.add_handler(CallbackQueryHandler(service_selected))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_text))

    print("Бот кор карда истодааст...")
    app.run_polling()


if __name__ == "__main__":
    main()
