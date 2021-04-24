# std
import http.client
import logging
import urllib.parse
from typing import List

# project
from . import Notifier, Event


class PushoverNotifier(Notifier):
    def __init__(self, title_prefix: str, config: dict):
        logging.info("Initializing Pushover notifier.")
        super().__init__(title_prefix, config)
        try:
            credentials = config["credentials"]
            self.token = credentials["api_token"]
            self.user = credentials["user_key"]
        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")

    def send_events_to_user(self, events: List[Event]) -> bool:
        errors = False
        for event in events:
            if event.type in self._notification_types and event.service in self._notification_services:
                conn = http.client.HTTPSConnection("api.pushover.net:443", timeout=self._conn_timeout_seconds)
                conn.request(
                    "POST",
                    "/1/messages.json",
                    urllib.parse.urlencode(
                        {
                            "token": self.token,
                            "user": self.user,
                            "title": self.get_title_for_event(event),
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

        return not errors
