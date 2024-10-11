import requests
import urllib.parse
import json

telegrambottoken = "7816362494:AAHgPjfUaso_c7igpi9z_PTZ7PBvEciv_2E"
telegrambotchatid = "5147662675"
def send_message(msg):
    try:
        payload = {
            'chat_id': telegrambotchatid,
            'text': msg,
            'parse_mode': 'HTML'  # Ensures that the message is parsed as HTML
        }
        send_text = f'https://api.telegram.org/bot{telegrambottoken}/sendMessage'
        request_response = requests.post(send_text, data=payload)
        loaded_response = json.loads(request_response.content.decode())
    except Exception as e:
        print(f"Error on send telegram message : {e}")
        return None
        