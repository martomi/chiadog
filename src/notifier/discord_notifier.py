# std
import http.client
import logging
import urllib.parse
import socket
from typing import List

# project
from . import Notifier, Event, EventType


class DiscordNotifier(Notifier):
    def __init__(self, title_prefix: str, config: dict):
        logging.info("Initializing Discord notifier.")
        super().__init__(title_prefix, config)
        try:
            self.webhook_url = config["webhook_url"]
        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")

    def send_events_to_user(self, events: List[Event]) -> bool:
        errors = False
        for event in events:
            if event.type == EventType.USER:
                o = urllib.parse.urlparse(self.webhook_url)
                conn = http.client.HTTPSConnection(o.netloc)
                conn.request(
                    "POST",
                    o.path,
                    urllib.parse.urlencode(
                        {
                            "username": f"chiadog on {socket.gethostname()}",
                            "content": event.message,
                        }
                    ),
                    {"Content-type": "application/x-www-form-urlencoded"},
                )
                response = conn.getresponse()
                if response.getcode() != 204:
                    logging.warning(f"Problem sending event to user, code: {response.getcode()}")
                    errors = True
                conn.close()

        return errors
