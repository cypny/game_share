import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from storage import bot_token

TOKEN = bot_token


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция обработки сообщений"""
    await update.message.reply_text("Сосал?")


def main():

    application = Application.builder().token(TOKEN).build()


    application.add_handler(MessageHandler(filters.ALL, echo))


    application.run_polling()


if __name__ == "__main__":
    main()