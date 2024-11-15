import requests
import urllib.parse
import json
import const


def send_message(msg):
    try:
        payload = {
            'chat_id': const.telegrambotchatid,
            'text': msg,
            'parse_mode': 'HTML'  # Ensures that the message is parsed as HTML
        }
        send_text = f'https://api.telegram.org/bot{const.telegrambottoken}/sendMessage'
        request_response = requests.post(send_text, data=payload)
        loaded_response = json.loads(request_response.content.decode())
    except Exception as e:
        print(f"Error on send telegram message : {e}")
        return None
        