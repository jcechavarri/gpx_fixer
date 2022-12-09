#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.
import os
from fix_gpx import fix_file

import logging
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters


PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def fix_gpx_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fix gpx file"""
    filename = update.message.document.file_name
    if not filename.endswith(".gpx"):
        await update.message.reply_text("Debes subir un archivo en formato GPX.")
    file = await context.bot.get_file(update.message.document)
    data = await file.download_as_bytearray()
    data = data.decode()
    lines = data.split("\n")
    fixed_file = "\n".join(fix_file(lines))
    bytes_file = bytes(fixed_file, "utf-8")
    await update.message.reply_document(
        document=bytes_file,
        caption="Arreglada! Ahora puedes subirla a strava. (https://www.strava.com/upload/select)",
        filename=filename
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.add_handler(MessageHandler(filters.ATTACHMENT & ~filters.COMMAND, fix_gpx_file))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()
    # application.run_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    # application.bot.setWebhook('https://gpx-fixer.herokuapp.com/' + TOKEN)

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print("ERROR:\n", e)
