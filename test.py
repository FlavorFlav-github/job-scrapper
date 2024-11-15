import telegram
import const


# Send the picture to telegram
bot = telegram.Bot(token=const.telegrambottoken)
bot.send_photo(chat_id=const.telegrambotchatid, photo="../linkedin-scrap-jobs-data/page_html_1 (2).png")