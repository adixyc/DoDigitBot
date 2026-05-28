# ==========================================
# DoDigitBot - Advanced Version
# Hosting: Render
# ==========================================

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

PRICE = "₹199"

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
    return "DoDigitBot Running"

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
# LOAD / SAVE
# ==========================================

def load_accounts():

    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_accounts(data):

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ==========================================
# CHECK CHANNEL JOIN
# ==========================================

def is_joined(user_id):

    try:

        member = bot.get_chat_member(
            CHANNEL_USERNAME,
            user_id
        )

        if member.status in [
            "member",
            "administrator",
            "creator"
        ]:
            return True

        return False

    except:
        return False

# ==========================================
# START
# ==========================================

@bot.message_handler(commands=['start'])
def start(message):

    if not is_joined(message.from_user.id):

        keyboard = types.InlineKeyboardMarkup()

        join_btn = types.InlineKeyboardButton(
            "📢 Join Channel",
            url="https://t.me/star_otps"
        )

        check_btn = types.InlineKeyboardButton(
            "✅ Check Again",
            callback_data="check_join"
        )

        keyboard.add(join_btn)
        keyboard.add(check_btn)

        bot.send_message(
            message.chat.id,
            "🚫 Join our channel first.",
            reply_markup=keyboard
        )

        return

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
        "🔒 Trusted Seller\n\n"
        "📦 Fresh Stock Available",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# ==========================================
# CALLBACKS
# ==========================================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):

    # ======================
    # CHECK JOIN
    # ======================

    if call.data == "check_join":

        if is_joined(call.from_user.id):

            start(call.message)

        else:

            bot.answer_callback_query(
                call.id,
                "❌ Join channel first."
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
    # BUY
    # ======================

    elif call.data == "buy":

        keyboard = types.InlineKeyboardMarkup(row_width=1)

        paid_btn = types.InlineKeyboardButton(
            "✅ I Have Paid",
            callback_data="paid"
        )

        copy_btn = types.InlineKeyboardButton(
            "📋 Copy UPI",
            url=f"https://upi://pay?pa={UPI_ID}"
        )

        channel_btn = types.InlineKeyboardButton(
            "📢 Join Channel",
            url="https://t.me/star_otps"
        )

        keyboard.add(paid_btn)
        keyboard.add(copy_btn)
        keyboard.add(channel_btn)

        caption = (
            f"💰 *Payment Details*\n\n"
            f"💵 Amount: {PRICE}\n"
            f"📲 UPI ID:\n`{UPI_ID}`\n\n"
            f"⚠️ After payment click below."
        )

        photo = open("qr.jpg", "rb")

        bot.send_photo(
            call.message.chat.id,
            photo,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    # ======================
    # PAID
    # ======================

    elif call.data == "paid":

        msg = bot.send_message(
            call.message.chat.id,
            "📨 Send your UTR / Transaction ID"
        )

        bot.register_next_step_handler(
            msg,
            verify_payment
        )

# ==========================================
# VERIFY PAYMENT
# ==========================================

def verify_payment(message):

    utr = message.text.strip()

    if len(utr) < 5:

        bot.send_message(
            message.chat.id,
            "❌ Invalid UTR."
        )

        return

    accounts = load_accounts()

    selected = None

    for acc in accounts:

        if not acc["sold"]:

            selected = acc
            break

    if selected is None:

        bot.send_message(
            message.chat.id,
            "❌ Out of stock."
        )

        return

    # ======================================
    # SEND UTR TO ADMIN
    # ======================================

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    approve_btn = types.InlineKeyboardButton(
        "✅ Approve",
        callback_data=f"approve_{message.from_user.id}"
    )

    reject_btn = types.InlineKeyboardButton(
        "❌ Reject",
        callback_data=f"reject_{message.from_user.id}"
    )

    keyboard.add(approve_btn, reject_btn)

    bot.send_message(
        ADMIN_ID,
        f"🛒 New Payment Request\n\n"
        f"👤 User ID: {message.from_user.id}\n"
        f"💳 UTR: {utr}",
        reply_markup=keyboard
    )

    # TEMP SAVE
    pending[str(message.from_user.id)] = selected

    bot.send_message(
        message.chat.id,
        "⏳ Payment verification pending.\n"
        "Admin will verify shortly."
    )

# ==========================================
# TEMP STORAGE
# ==========================================

pending = {}

# ==========================================
# APPROVE / REJECT
# ==========================================

@bot.callback_query_handler(func=lambda call:
    call.data.startswith("approve_") or
    call.data.startswith("reject_"))
def admin_actions(call):

    # ======================
    # APPROVE
    # ======================

    if call.data.startswith("approve_"):

        user_id = call.data.split("_")[1]

        if user_id not in pending:

            bot.answer_callback_query(
                call.id,
                "Expired."
            )
            return

        selected = pending[user_id]

        accounts = load_accounts()

        for acc in accounts:

            if acc["phone"] == selected["phone"]:

                acc["sold"] = True

        save_accounts(accounts)

        bot.send_message(
            int(user_id),
            f"✅ Payment Approved\n\n"
            f"📱 Phone:\n"
            f"`{selected['phone']}`\n\n"
            f"🔑 Password:\n"
            f"`{selected['password']}`\n\n"
            f"🔐 2FA:\n"
            f"`{selected['twofa']}`\n\n"
            f"⚠️ Change details immediately.",
            parse_mode="Markdown"
        )

        del pending[user_id]

        bot.edit_message_text(
            "✅ Approved",
            call.message.chat.id,
            call.message.message_id
        )

    # ======================
    # REJECT
    # ======================

    elif call.data.startswith("reject_"):

        user_id = call.data.split("_")[1]

        bot.send_message(
            int(user_id),
            "❌ Payment Rejected.\n"
            "Contact support."
        )

        if user_id in pending:
            del pending[user_id]

        bot.edit_message_text(
            "❌ Rejected",
            call.message.chat.id,
            call.message.message_id
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
