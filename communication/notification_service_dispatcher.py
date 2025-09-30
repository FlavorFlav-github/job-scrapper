import logging

from communication.notification_service_telegram import TelegramSender
from const import NOTIFICATION_CHANNELS

logger = logging.getLogger(__name__)

# A simple map to link channel names to their concrete sender classes
SENDER_MAP = {
    "telegram": TelegramSender,
    # "slack": SlackSender,  # Add others here
    # "email": EmailSender,
}


def send_event(content, content_type='text'):
    """Centralized function to send an event via configured channels."""

    active_channels = NOTIFICATION_CHANNELS  # Load your configuration

    for channel_name, channel_config in active_channels.items():

        # Check if the channel is enabled AND a sender exists for it
        if channel_config.get('enabled') and channel_name in SENDER_MAP:

            # 1. Get the Sender class
            SenderClass = SENDER_MAP[channel_name]

            # 2. Instantiate it
            sender_instance = SenderClass()

            # 3. Call the generic send method
            sender_instance.send(content, content_type, channel_config)

        elif channel_config.get('enabled'):
            logger.warning(f"Warning: No sender implemented for enabled channel: {channel_name}")