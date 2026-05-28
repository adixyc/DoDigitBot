# ==========================================
# DoDigitBot - Full Telegram Bot
# Hosting: Render
# ==========================================

# INSTALL:
# pip install pyTelegramBotAPI flask

import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os
import json

# ==========================================
# CONFIG
# ==========================================

BOT_TOKEN = "8744043515:AAEqv8G4yDLEsutTZZR0l4PpFuCtrlwyEqE"

ADMIN_ID = 6308333888

CHANNEL_USERNAME = "@star_otps"

UPI_ID = "paytm.s255mng@pty"

# ==========================================
# BOT
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# FLASK SERVER
# ==========================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Running"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# DATABASE
# ==========================================

DB_FILE = "accounts.json"

if not os.path.exists(DB_FILE):

    sample = [
        {
            "phone": "+919999999999",
            "password": "pass123",
            "twofa": "2fa123",
            "sold": False
        }
    ]

    with open(DB_FILE, "w") as f:
        json.dump(sample, f, indent=4)

# ==========================================
# LOAD DATABASE
# ==========================================

def load_accounts():

    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_accounts(data):

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ==========================================
# START
# ==========================================

@bot.message_handler(commands=['start'])
def start(message):

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    buy_btn = types.InlineKeyboardButton(
        "🛒 Buy Accounts",
        callback_data="buy"
    )

    stock_btn = types.InlineKeyboardButton(
        "📦 Stock",
        callback_data="stock"
    )

    channel_btn = types.InlineKeyboardButton(
        "📢 Channel",
        url="https://t.me/star_otps"
    )

    support_btn = types.InlineKeyboardButton(
        "🆘 Support",
        url="https://t.me/swappinge_wife"
    )

    keyboard.add(buy_btn, stock_btn)
    keyboard.add(channel_btn, support_btn)

    bot.send_message(
        message.chat.id,
        "🚀 *DoDigitBot*\n\n"
        "💎 Premium Telegram Accounts\n"
        "⚡ Instant Delivery\n"
        "🔒 Trusted Seller",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# ==========================================
# CALLBACKS
# ==========================================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):

    # ======================
    # BUY
    # ======================

    if call.data == "buy":

        keyboard = types.InlineKeyboardMarkup()

        paid_btn = types.InlineKeyboardButton(
            "✅ I Have Paid",
            callback_data="paid"
        )

        keyboard.add(paid_btn)

        bot.send_message(
            call.message.chat.id,
            f"💰 Price: ₹199\n\n"
            f"📲 UPI ID:\n"
            f"`{UPI_ID}`",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    # ======================
    # STOCK
    # ======================

    elif call.data == "stock":

        accounts = load_accounts()

        available = len(
            [x for x in accounts if not x["sold"]]
        )

        bot.send_message(
            call.message.chat.id,
            f"📦 Available Accounts: {available}"
        )

    # ======================
    # PAID
    # ======================

    elif call.data == "paid":

        accounts = load_accounts()

        selected = None

        for acc in accounts:

            if not acc["sold"]:
                selected = acc
                break

        if selected is None:

            bot.send_message(
                call.message.chat.id,
                "❌ Out of stock."
            )

            return

        # MARK SOLD
        for acc in accounts:

            if acc["phone"] == selected["phone"]:
                acc["sold"] = True

        save_accounts(accounts)

        # SEND ACCOUNT
        bot.send_message(
            call.message.chat.id,
            f"✅ Payment Confirmed\n\n"
            f"📱 Phone:\n"
            f"`{selected['phone']}`\n\n"
            f"🔑 Password:\n"
            f"`{selected['password']}`\n\n"
            f"🔐 2FA:\n"
            f"`{selected['twofa']}`",
            parse_mode="Markdown"
        )

        # ADMIN LOG
        bot.send_message(
            ADMIN_ID,
            f"🛒 New Sale\n\n"
            f"User: {call.from_user.id}\n"
            f"Account: {selected['phone']}"
        )

# ==========================================
# ADD ACCOUNT
# ==========================================

@bot.message_handler(commands=['add'])
def add_account(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        data = message.text.split("\n")

        phone = data[1]
        password = data[2]
        twofa = data[3]

        accounts = load_accounts()

        accounts.append({
            "phone": phone,
            "password": password,
            "twofa": twofa,
            "sold": False
        })

        save_accounts(accounts)

        bot.send_message(
            message.chat.id,
            "✅ Account Added"
        )

    except:

        bot.send_message(
            message.chat.id,
            "/add\nphone\npassword\n2fa"
        )

# ==========================================
# RUN
# ==========================================

print("Bot Running...")

keep_alive()

bot.infinity_polling()
