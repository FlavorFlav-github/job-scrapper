import requests
import logging

from communication.notification_service_abstract import MessageSender

logger = logging.getLogger(__name__)

class TelegramSender(MessageSender):
    def send(self, content, content_type, config):
        """Implements the Telegram message sending logic."""

        # Extract specific Telegram config
        token = config.get('token')
        chat_id = config.get('chat_id')

        try:
            if content_type == 'text':
                payload = {
                    'chat_id': chat_id,
                    'text': content,
                    'parse_mode': 'HTML'
                }
                url = f'https://api.telegram.org/bot{token}/sendMessage'
                requests.post(url, data=payload)
            elif content_type == 'image':
                # Assuming 'content' is the image path/URL for 'sendPhoto'
                payload = {'chat_id': chat_id}
                url = f'https://api.telegram.org/bot{token}/sendPhoto'

                # Note: Handling file opening/sending is platform-specific.
                # This example assumes 'content' is a local file path.
                with open(content, 'rb') as image_file:
                    requests.post(url, data=payload, files={'photo': image_file})

            # Add robust error checking and logging here
            logger.info(f"Message sent successfully to Telegram.")

        except Exception as e:
            logger.warning(f"Error sending message to Telegram: {e}")