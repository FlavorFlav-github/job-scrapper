from abc import ABC, abstractmethod

class MessageSender(ABC):
    """Abstract Base Class for all notification channels."""

    @abstractmethod
    def send(self, content, content_type, config):
        """Sends the content via the specific channel."""
        pass