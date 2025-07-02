import telebot
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import os

# === Токен Telegram-бота ===
BOT_TOKEN = os.environ['BOT_TOKEN']
bot = telebot.TeleBot(BOT_TOKEN)

print("🚀 Бот запущен и ждёт сообщения...")

# === Google Sheets настройки ===
SPREADSHEET_ID = '1OyNN8vZuLD1JHTTCYZIYQcNq3cdA1BtsmvdL4qSHNY0'
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# ✅ Читаем credentials.json из Secret Files
creds = ServiceAccountCredentials.from_json_keyfile_name('/etc/secrets/credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

print("✅ Таблица найдена, работаем с sheet1")

# === Обработчик сообщений с фото ===
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    print("📸 Пришло фото")

    caption = message.caption or ""
    try:
        qty_str, machine_str, stitches_str = caption.strip().split(',')
        qty = int(qty_str)
        machine = machine_str.strip().lower().replace('м', '')
        stitches = int(stitches_str)
    except Exception:
        qty = "❌"
        machine = "❌"
        stitches = "❌"

    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    download_url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}'
    image_formula = f'=IMAGE("{download_url}")'

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = message.from_user.username or message.from_user.first_name
    stitches_total = int(qty) * int(stitches) if qty != "❌" and stitches != "❌" else "❌"

    row_data = [timestamp, user, image_formula, machine, qty, stitches, stitches_total]
    row_index = len(sheet.get_all_values()) + 1

    try:
        for col_index, value in enumerate(row_data, start=1):
            sheet.update_cell(row_index, col_index, value)
        print("✅ Строка добавлена в таблицу")
    except Exception as e:
        print("❌ Ошибка при добавлении строки в таблицу:", e)

    bot.reply_to(message, "✅ Отчёт принят!")

bot.polling()
