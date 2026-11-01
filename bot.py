import json
import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

DATA_FILE = "users.json"

# Состояния для пошагового ввода
GET_NAME = 1
GET_COLOR = 2


def load_users() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_users(users: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


users = load_users()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_keyboard = [
        ["✍️ Сохранить данные", "👤 Мой профиль"],
        ["❓ Помощь"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "👋 Привет! Используй кнопки меню ниже 👇",
        reply_markup=markup
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user_id = str(update.effective_user.id)

    current_state = context.user_data.get("state")

    if current_state == GET_NAME:
        context.user_data["temp_name"] = text
        context.user_data["state"] = GET_COLOR
        await update.message.reply_text("🎨 Теперь введи любимый цвет:")
        return

    elif current_state == GET_COLOR:
        name = context.user_data.get("temp_name")
        color = text

        users[user_id] = {
            "name": name,
            "color": color
        }
        save_users(users)

        context.user_data["state"] = None

        await update.message.reply_text("✅ Сохранено!")
        await update.message.reply_text(
            f"👤 Профиль:\n\n"
            f"👤 Имя: {name}\n"
            f"🎨 Цвет: {color}"
        )
        return

    if text == "✍️ Сохранить данные":
        context.user_data["state"] = GET_NAME
        await update.message.reply_text("✍️ Введи своё имя:")

    elif text == "👤 Мой профиль":
        if user_id in users:
            p_name = users[user_id].get("name")
            p_color = users[user_id].get("color")
            await update.message.reply_text(
                f"📋 Профиль:\n\n"
                f"👤 Имя: {p_name}\n"
                f"🎨 Цвет: {p_color}"
            )
        else:
            await update.message.reply_text("У тебя ещё нет сохранённых данных. Нажми «✍️ Сохранить данные».")

    elif text == "❓ Помощь":
        await update.message.reply_text(
            "Используй кнопки меню 👇",
            reply_markup=ReplyKeyboardMarkup([
                ["✍️ Сохранить данные", "👤 Мой профиль"],
                ["❓ Помощь"]
            ], resize_keyboard=True)
        )

    else:
        await update.message.reply_text("Используй кнопки меню 👇")

from dotenv import load_dotenv
import os
load_dotenv()
 
def main() -> None:
    TOKEN = os.environ.get('TOKEN')

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.info("Бот запущен!")
    application.run_polling()


if __name__ == "__main__":
    main()