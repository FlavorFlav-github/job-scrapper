import requests
import urllib.parse
import json
import const


def send_message(msg=None, image_url=None):
    try:
        if image_url is None and msg is not None:
            payload = {
                'chat_id': const.telegrambotchatid,
                'text': msg,
                'parse_mode': 'HTML'  # Ensures that the message is parsed as HTML
            }
            send_text = f'https://api.telegram.org/bot{const.telegrambottoken}/sendMessage'
            request_response = requests.post(send_text, data=payload)
            loaded_response = json.loads(request_response.content.decode())
        if image_url is not None and msg is None:
            payload = {
                'chat_id': const.telegrambotchatid
            }
            send_text = f'https://api.telegram.org/bot{const.telegrambottoken}/sendPhoto'
            request_response = requests.post(send_text, data=payload, files={'media': open(image_url, 'rb')})
            loaded_response = json.loads(request_response.content.decode())
            print(loaded_response)
    except Exception as e:
        print(f"Error on send telegram message : {e}")
        return None
        