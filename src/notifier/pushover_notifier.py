# std
import http.client
import logging
import urllib.parse
from typing import List

# project
from . import Notifier, Event, EventType


class PushoverNotifier(Notifier):
    def __init__(self, title_prefix: str, config: dict):
        logging.info("Initializing Pushover notifier.")
        super().__init__(title_prefix, config)
        try:
            self.token = config["api_token"]
            self.user = config["user_key"]
        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")

    def send_events_to_user(self, events: List[Event]) -> bool:
        errors = False
        for event in events:
            if event.type == EventType.USER:
                conn = http.client.HTTPSConnection("api.pushover.net:443")
                conn.request(
                    "POST",
                    "/1/messages.json",
                    urllib.parse.urlencode(
                        {
                            "token": self.token,
                            "user": self.user,
                            "title": f"{self._title_prefix} {event.service.name}",
                            "message": event.message,
                            "priority": event.priority.value,
                        }
                    ),
                    {"Content-type": "application/x-www-form-urlencoded"},
                )
                response = conn.getresponse()
                if response.getcode() != 200:
                    logging.warning(f"Problem sending event to user, code: {response.getcode()}")
                    errors = True
                conn.close()

        return errors
