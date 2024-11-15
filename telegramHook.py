import const
import json
from telegram import Update
from telegram.ext import CommandHandler, Application, ContextTypes, MessageHandler


async def wait_captcha_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) > 0:
        raw_param = context.args[0]
        if "image" in raw_param:
            with open("../linkedin-scrap-jobs-data/captcha_check.json", "w") as f:
                json.dump({"img_name": raw_param}, f)


def main() -> None:
    application = Application.builder().token(const.telegrambottoken).build()

    application.add_handler(CommandHandler("captcha_check", wait_captcha_response, has_args=True))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
