import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import logging

# Replace with your Telegram Bot Token
TELEGRAM_BOT_TOKEN = "7983817547:AAGNLbQoa4KuTvksdIFwh_PbA5Z8UwXD4VA"

# Replace with your Telegram User ID
ADMIN_ID = 6317271346  # Example: 123456789
ADMIN_USERNAME = "@Dhruv0757"

# Store approved users
approved_users = set()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def luhn_checksum(card_number):
    """Calculate Luhn checksum for a credit card number."""
    digits = [int(d) for d in card_number]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10

def is_valid_credit_card(card_number):
    """Check if a credit card number is valid using the Luhn algorithm."""
    return luhn_checksum(card_number) == 0

def generate_credit_card(prefix, length=16):
    """Generate a valid credit card number with the given prefix."""
    card_number = [int(d) for d in str(prefix)]
    while len(card_number) < length - 1:
        card_number.append(random.randint(0, 9))
    
    # Calculate the last digit (checksum)
    checksum = (10 - luhn_checksum(card_number + [0])) % 10
    card_number.append(checksum)
    
    return "".join(map(str, card_number))

# Restrict access to admin and approved users
def restricted(func):
    def wrapper(update: Update, context: CallbackContext):
        user_id = update.message.from_user.id
        username = update.message.from_user.username or "No Username"

        if user_id == ADMIN_ID or user_id in approved_users:
            return func(update, context)
        else:
            update.message.reply_text(f"🚫 Access Denied! Please request access from the admin: {ADMIN_USERNAME}.")
            
            # Notify admin about the request
            context.bot.send_message(
                chat_id=ADMIN_ID, 
                text=f"🔔 Access request from user:\nID: {user_id}\nUsername: @{username}\n\nApprove with: /approve {user_id}"
            )
    return wrapper

# Approve users
def approve(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        update.message.reply_text("🚫 Only the admin can approve users.")
        return

    try:
        user_id = int(context.args[0])
        approved_users.add(user_id)
        update.message.reply_text(f"✅ User {user_id} has been approved!")
    except (IndexError, ValueError):
        update.message.reply_text("⚠️ Please provide a valid user ID. Example: /approve 123456789")

# Telegram Bot Handlers
def start(update: Update, context: CallbackContext):
    update.message.reply_text(f"Hello! This bot requires admin approval to use.\n\n"
                              "Commands:\n"
                              "/check <card_number> - Validate a credit card number\n"
                              "/generate <prefix> - Generate a valid credit card number (e.g., /generate 4)\n"
                              "/approve <user_id> (Admin Only) - Approve a user\n\n"
                              f"To get access, contact {ADMIN_USERNAME}.")

@restricted
def check_card(update: Update, context: CallbackContext):
    try:
        card_number = context.args[0]
        if is_valid_credit_card(card_number):
            update.message.reply_text(f"✅ The card number {card_number} is valid.")
        else:
            update.message.reply_text(f"❌ The card number {card_number} is NOT valid.")
    except IndexError:
        update.message.reply_text("⚠️ Please provide a card number. Example: /check 4539578763621486")

@restricted
def generate_card(update: Update, context: CallbackContext):
    try:
        prefix = int(context.args[0])
        new_card = generate_credit_card(prefix, 16)
        update.message.reply_text(f"🎉 Generated Credit Card: {new_card}\n\nThis number is valid based on the Luhn algorithm.")
    except (IndexError, ValueError):
        update.message.reply_text("⚠️ Please provide a prefix (e.g., Visa starts with 4). Example: /generate 4")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("approve", approve))
    dp.add_handler(CommandHandler("check", check_card))
    dp.add_handler(CommandHandler("generate", generate_card))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
    