import os
import psycopg2
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

app = Flask(__name__)

# إعداد قاعدة البيانات
DATABASE_URL = os.getenv('postgres://reward_db_6744_user:9JafL71tVDrsGmrjYa4hiRnHNhNWAoZW@dpg-cpoeicqj1k6c73a67klg-a.virginia-postgres.render.com/reward_db_6744')
API_TOKEN = os.getenv('7157789286:AAFVBQgNYHORN-q-R-RmjE8CHrf9aGAaH_s')
RENDER_EXTERNAL_HOSTNAME = os.getenv('postgres://reward_db_6744_user:9JafL71tVDrsGmrjYa4hiRnHNhNWAoZW@dpg-cpoeicqj1k6c73a67klg-a.virginia-postgres.render.com/reward_db_6744')
PORT = int(os.getenv('PORT', 10000))

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            points INTEGER DEFAULT 0
        );
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task_id SERIAL PRIMARY KEY,
            description TEXT,
            points INTEGER
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

# أوامر البوت
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO users (telegram_id) VALUES (%s) ON CONFLICT (telegram_id) DO NOTHING', (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    update.message.reply_text('مرحباً! أنا بوت النقاط. استخدم /points لمعرفة نقاطك.')

def points(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT points FROM users WHERE telegram_id = %s', (user_id,))
    points = cur.fetchone()[0]
    cur.close()
    conn.close()
    update.message.reply_text(f'لديك {points} نقطة.')

def tasks(update: Update, context: CallbackContext):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT task_id, description, points FROM tasks')
    tasks = cur.fetchall()
    cur.close()
    conn.close()

    keyboard = [
        [InlineKeyboardButton(f'{task[1]} - {task[2]} نقطة', callback_data=f'complete_{task[0]}')] for task in tasks
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('اختر مهمة لإتمامها:', reply_markup=reply_markup)

def complete_task(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    task_id = int(query.data.split('_')[1])
    user_id = query.from_user.id

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT points FROM tasks WHERE task_id = %s', (task_id,))
    task_points = cur.fetchone()[0]
    cur.execute('UPDATE users SET points = points + %s WHERE telegram_id = %s', (task_points, user_id))
    conn.commit()
    cur.close()
    conn.close()
    query.edit_message_text('تم إكمال المهمة! تم إضافة النقاط إلى رصيدك.')

# إعداد البوت
def main():
    create_tables()
    TOKEN = API_TOKEN
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("points", points))
    dp.add_handler(CommandHandler("tasks", tasks))
    dp.add_handler(CallbackQueryHandler(complete_task, pattern='^complete_'))

    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.set_webhook(f"https://{RENDER_EXTERNAL_HOSTNAME}/{TOKEN}")

    app.run(host='0.0.0.0', port=PORT)

@app.route('/')
def home():
    return 'Hello, this is the PointBot!'

if __name__ == '__main__':
    main()
