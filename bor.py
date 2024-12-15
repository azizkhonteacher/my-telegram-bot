from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from datetime import datetime

# Savol yuborish uchun flag
ASK_QUESTION_STATE = {}

# Ro'yxatni saqlash
users_list = []  # Foydalanuvchi ma'lumotlarini saqlash (user_id, ism, familiya, username)
questions_list = []  # Savollar ro'yxatini saqlash

# Admin ID (o'zingizning Telegram ID yoki boshqa adminning ID si)
ADMIN_ID = 750589627  # O'zingizning Telegram user ID ni qo'ying

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users_list.append({
        "first_name": user.first_name,
        "last_name": user.last_name if user.last_name else "Noma'lum",
        "username": f"@{user.username}" if user.username else "Noma'lum",
        "user_id": user.id
    })  # Foydalanuvchini ro'yxatga qo'shamiz

    # Asosiy menyu tugmalari
    keyboard = [
        [InlineKeyboardButton("👤 Men haqimda", callback_data="about")],
        [InlineKeyboardButton("❓ Savol berish", callback_data="ask_question")],
        [InlineKeyboardButton("🌐 Saytga o'tish", url="https://azizkhon-resume.netlify.app/")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:  # Start komandasi orqali yuborilgan
        await update.message.reply_text(
            "🔍 Quyidagilardan birini tanlang:",
            reply_markup=reply_markup
        )
    elif update.callback_query:  # Callback orqali qayta chiqish
        await update.callback_query.edit_message_text(
            "🔍 Quyidagilardan birini tanlang:",
            reply_markup=reply_markup
        )

# Callback tugmalarni boshqarish
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Tugma tanlangan holatlar
    if query.data == "about":
        await query.edit_message_text(
            "👤 Men haqimda:\n\nAssalomu alaykum! Bu bot orqali menga savol berishingiz yoki saytimga o'tishingiz mumkin.",
            reply_markup=back_to_menu()
        )
    elif query.data == "ask_question":
        # Foydalanuvchi holatini savol berish rejimiga o'tkazamiz
        user_id = query.from_user.id
        ASK_QUESTION_STATE[user_id] = True

        await query.edit_message_text(
            "❓ Savolingizni yuboring. Yuborganingizdan so'ng yana menyuga qaytasiz.",
        )
    elif query.data == "back":
        await start(update, context)  # Asosiy menyuni qayta chiqarish

# Foydalanuvchi savol yuborganda
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Foydalanuvchi savol rejimida bo'lsa
    if ASK_QUESTION_STATE.get(user_id):
        savol = update.message.text
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Savol yuborilgan vaqt

        # Savolni saqlash
        questions_list.append({
            "user_id": user_id,
            "username": update.message.from_user.username,
            "question": savol,
            "timestamp": timestamp
        })

        # Admin yoki foydalanuvchi logi uchun savolni qayd qilish
        print(f"Yangi savol: {savol} (Yuboruvchi: {update.message.from_user.username}, Vaqt: {timestamp})")

        # Savol holatini o‘chiramiz
        ASK_QUESTION_STATE[user_id] = False

        # Savolni adminga yuborish
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Yangi savol yuborildi!\n\nSavol: {savol}\nYuboruvchi: {update.message.from_user.username}\nVaqt: {timestamp}"
        )

        # Foydalanuvchiga javob yuboramiz va asosiy menyuni chiqaramiz
        await update.message.reply_text(
            "✅ Savolingiz yuborildi!",
        )
        await start(update, context)  # Asosiy menyuni qayta chiqarish
    else:
        # Foydalanuvchi savol rejimida bo'lmasa, xabarni e'tiborsiz qoldiramiz
        await update.message.reply_text("❗ Iltimos, tugmalardan birini tanlang yoki /start ni yuboring.")

# Ortga qaytish tugmasi uchun yordamchi funksiya
def back_to_menu():
    keyboard = [
        [InlineKeyboardButton("⬅️ Asosiy menyuga qaytish", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Foydalanuvchilar ro'yxatini yuborish komandasi
async def send_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if users_list:
        user_list_text = "Foydalanuvchilar ro'yxati:\n"
        for user in users_list:
            user_list_text += (
                f"Ism: {user['first_name']}\n"
                f"Familiya: {user['last_name']}\n"
                f"Username: {user['username']}\n"
                f"User ID: {user['user_id']}\n\n"
            )
        # Adminga foydalanuvchilar ro'yxatini yuborish
        await context.bot.send_message(chat_id=ADMIN_ID, text=user_list_text)
        await update.message.reply_text("Foydalanuvchilar ro'yxati yuborildi!")
    else:
        await update.message.reply_text("Hali hech kim start bosmadi.")

# Savollar ro'yxatini yuborish komandasi
async def send_questions_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if questions_list:
        questions_text = "Yuborilgan savollar:\n"
        for question in questions_list:
            questions_text += (
                f"Yuboruvchi: {question['username']}\n"
                f"Vaqt: {question['timestamp']}\n"
                f"Savol: {question['question']}\n\n"
            )
        # Adminga savollar ro'yxatini yuborish
        await context.bot.send_message(chat_id=ADMIN_ID, text=questions_text)
        await update.message.reply_text("Savollar ro'yxati yuborildi!")
    else:
        await update.message.reply_text("Hali hech qanday savol yuborilmadi.")

# Botni ishga tushirish
if __name__ == "__main__":
    app = ApplicationBuilder().token("5823266460:AAFqEolnXwLKifffW-LBf96mISdSLcK7t_I").build()  # Tokenni almashtiring

    # Handlerlarni qo'shish
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("send_users", send_users_list))  # /send_users komandasi
    app.add_handler(CommandHandler("send_questions", send_questions_list))  # /send_questions komandasi

    # Botni ishga tushirish
    print("Bot ishga tushdi...")
    app.run_polling()
