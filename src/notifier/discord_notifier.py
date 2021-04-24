# std
import http.client
import logging
import urllib.parse
from typing import List

# project
from . import Notifier, Event


class DiscordNotifier(Notifier):
    def __init__(self, title_prefix: str, config: dict):
        logging.info("Initializing Discord notifier.")
        super().__init__(title_prefix, config)
        try:
            credentials = config["credentials"]
            self.webhook_url = credentials["webhook_url"]
        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")

    def send_events_to_user(self, events: List[Event]) -> bool:
        errors = False
        for event in events:
            if event.type in self._notification_types and event.service in self._notification_services:
                o = urllib.parse.urlparse(self.webhook_url)
                conn = http.client.HTTPSConnection(o.netloc, timeout=self._conn_timeout_seconds)
                conn.request(
                    "POST",
                    o.path,
                    urllib.parse.urlencode(
                        {
                            "username": "chiadog",
                            "content": f"**{self.get_title_for_event(event)}**\n{event.message}",
                        }
                    ),
                    {"Content-type": "application/x-www-form-urlencoded"},
                )
                response = conn.getresponse()
                if response.getcode() != 204:
                    logging.warning(f"Problem sending event to user, code: {response.getcode()}")
                    errors = True
                conn.close()

        return not errors
