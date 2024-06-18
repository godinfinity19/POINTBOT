import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import psycopg2

# إعداد الاتصال بقاعدة البيانات
conn = psycopg2.connect(
    "postgres://reward_db_6744_user:9JafL71tVDrsGmrjYa4hiRnHNhNWAoZW@dpg-cpoeicqj1k6c73a67klg-a.virginia-postgres.render.com/reward_db_6744"
)
cur = conn.cursor()

# إعداد تسجيل الدخول
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# تعريف البوت
API_TOKEN = '7157789286:AAFVBQgNYHORN-q-R-RmjE8CHrf9aGAaH_s'
updater = Updater(token=API_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# دالة بدء البوت
def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    cur.execute("INSERT INTO users (chat_id) VALUES (%s) ON CONFLICT (chat_id) DO NOTHING;", (chat_id,))
    conn.commit()
    update.message.reply_text('مرحبًا! لقد تم تسجيلك بنجاح. استخدم /points لعرض نقاطك.')

# دالة عرض النقاط
def points(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    cur.execute("SELECT points FROM users WHERE chat_id = %s;", (chat_id,))
    points = cur.fetchone()[0]
    update.message.reply_text(f'لديك {points} نقطة.')

# دالة عرض المهام
def tasks(update: Update, context: CallbackContext) -> None:
    cur.execute("SELECT task_id, description, points FROM tasks;")
    tasks = cur.fetchall()
    if tasks:
        task_list = "\n".join([f"{task[1]} - {task[2]} نقطة" for task in tasks])
        update.message.reply_text(f'المهام المتاحة:\n{task_list}')
    else:
        update.message.reply_text('لا توجد مهام متاحة حالياً.')

# دالة إكمال المهام
def complete(update: Update, context: CallbackContext) -> None:
    task_id = int(context.args[0])
    chat_id = update.message.chat_id

    # تحقق من وجود المهمة
    cur.execute("SELECT points FROM tasks WHERE task_id = %s;", (task_id,))
    task = cur.fetchone()
    if task:
        task_points = task[0]
        # تحديث نقاط المستخدم
        cur.execute("UPDATE users SET points = points + %s WHERE chat_id = %s;", (task_points, chat_id))
        conn.commit()
        update.message.reply_text(f'تم إكمال المهمة بنجاح! لقد حصلت على {task_points} نقطة.')
    else:
        update.message.reply_text('المهمة غير موجودة.')

# دالة عرض الخدمات
def services(update: Update, context: CallbackContext) -> None:
    cur.execute("SELECT service_id, description, points_required FROM services;")
    services = cur.fetchall()
    if services:
        service_list = "\n".join([f"{service[1]} - {service[2]} نقطة" for service in services])
        update.message.reply_text(f'الخدمات المتاحة:\n{service_list}')
    else:
        update.message.reply_text('لا توجد خدمات متاحة حالياً.')

# دالة استبدال النقاط بالخدمات
def redeem(update: Update, context: CallbackContext) -> None:
    service_id = int(context.args[0])
    chat_id = update.message.chat_id

    # تحقق من وجود الخدمة
    cur.execute("SELECT points_required FROM services WHERE service_id = %s;", (service_id,))
    service = cur.fetchone()
    if service:
        points_required = service[0]
        # تحقق من نقاط المستخدم
        cur.execute("SELECT points FROM users WHERE chat_id = %s;", (chat_id,))
        user_points = cur.fetchone()[0]
        if user_points >= points_required:
            # تحديث نقاط المستخدم
            cur.execute("UPDATE users SET points = points - %s WHERE chat_id = %s;", (points_required, chat_id))
            conn.commit()
            update.message.reply_text(f'تم استبدال النقاط بنجاح! لقد استخدمت {points_required} نقطة.')
        else:
            update.message.reply_text('ليس لديك نقاط كافية.')
    else:
        update.message.reply_text('الخدمة غير موجودة.')

# إعداد معالجات الأوامر
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("points", points))
dispatcher.add_handler(CommandHandler("tasks", tasks))
dispatcher.add_handler(CommandHandler("complete", complete))
dispatcher.add_handler(CommandHandler("services", services))
dispatcher.add_handler(CommandHandler("redeem", redeem))

# بدء البوت
updater.start_polling()
updater.idle()