import mysql.connector
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# MySQL ulanishini yaratish
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",  # MySQL server manzili
            user="root",       # MySQL foydalanuvchisi
            password="your_password",  # MySQL paroli
            database="telegram_bot"    # Baza nomi
        )
        if connection.is_connected():
            print("MySQL serveriga ulanish muvaffaqiyatli!")
            return connection
    except mysql.connector.Error as err:
        print(f"Xatolik: {err}")
        return None

# /start komandasini boshqarish
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Foydalanuvchini bazaga qo'shish
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (user_id, first_name, last_name, username) "
            "VALUES (%s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE user_id=user_id", 
            (user.id, user.first_name, user.last_name if user.last_name else "Noma'lum", user.username if user.username else "Noma'lum")
        )
        connection.commit()
        cursor.close()
        connection.close()

    # Asosiy menyu tugmalari
    keyboard = [
        [InlineKeyboardButton("👤 Men haqimda", callback_data="about")],
        [InlineKeyboardButton("❓ Savol berish", callback_data="ask_question")],
        [InlineKeyboardButton("🌐 Saytga o'tish", url="https://azizkhon-resume.netlify.app/")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            "🔍 Quyidagilardan birini tanlang:",
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            "🔍 Quyidagilardan birini tanlang:",
            reply_markup=reply_markup
        )

    # 2-adminga foydalanuvchi haqidagi ma'lumotlarni yuborish
    second_admin_id = 765274780  # 2-adminga yuboriladigan ID ni qo'yish
    await context.bot.send_message(
        chat_id=second_admin_id,
        text=f"Yangi foydalanuvchi: {user.first_name} {user.last_name if user.last_name else ''}\n"
             f"Username: @{user.username if user.username else 'Nomalum'}\n"
             f"User ID: {user.id}"
    )

# Admin ro'yxatini yuborish
async def send_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Faqat admin uchun
    if update.message.from_user.id == 750589627:  # O'zingizning admin ID ni qo'ying
        connection = create_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users")  # Foydalanuvchilar ro'yxatini olish
            users = cursor.fetchall()
            connection.close()

            if users:
                user_list_text = "Foydalanuvchilar ro'yxati:\n"
                for user in users:
                    user_list_text += (
                        f"Ism: {user['first_name']}\n"
                        f"Familiya: {user['last_name']}\n"
                        f"Username: {user['username']}\n"
                        f"User ID: {user['user_id']}\n"
                        f"Qo'shilgan vaqt: {user['date_joined']}\n\n"
                    )
                await update.message.reply_text(user_list_text)
            else:
                await update.message.reply_text("Hali hech kim start bosmagan.")
        else:
            await update.message.reply_text("Ma'lumotlar bazasi bilan ulanishda xatolik yuz berdi.")
    else:
        await update.message.reply_text("Siz bu komandani bajarish huquqiga ega emassiz.")

# Botni ishga tushirish
if __name__ == "__main__":
    app = Application.builder().token("5823266460:AAFqEolnXwLKifffW-LBf96mISdSLcK7t_I").build()

    # Handlerlarni qo'shish
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send_users", send_users_list))  # Admin uchun foydalanuvchilar ro'yxati komandasi

    # Botni ishga tushirish
    print("Bot ishga tushdi...")
    app.run_polling()
