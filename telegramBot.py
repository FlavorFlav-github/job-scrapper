import requests
import urllib.parse
import json
import const


def send_message(msg=None, file=None):
    try:
        if file is None and msg is not None:
            payload = {
                'chat_id': const.telegrambotchatid,
                'text': msg,
                'parse_mode': 'HTML'  # Ensures that the message is parsed as HTML
            }
            send_text = f'https://api.telegram.org/bot{const.telegrambottoken}/sendMessage'
            request_response = requests.post(send_text, data=payload)
            loaded_response = json.loads(request_response.content.decode())
        if file is not None and msg is None:
            payload = {
                'chat_id': const.telegrambotchatid
            }
            send_text = f'https://api.telegram.org/bot{const.telegrambottoken}/sendPhoto'
            request_response = requests.post(send_text, data=payload, files=file)
            loaded_response = json.loads(request_response.content.decode())
    except Exception as e:
        print(f"Error on send telegram message : {e}")
        return None
        