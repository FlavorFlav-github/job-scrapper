import const
import json
from telegram import Update
from telegram.ext import CommandHandler, Application, ContextTypes


def wait_captcha_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "image" in update.message.text:
        with open("../linkedin-scrap-jobs-data/captcha_check.json", "w") as f:
            json.dump({"img_name": update.message.text}, f)


def main() -> None:
    environment = const.env + "_" + const.server
    application = Application.builder().token(const.telegrambottoken).build()

    application.add_handler(CommandHandler(None, wait_captcha_response, has_args=False))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
