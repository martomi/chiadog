# std
import http.client
import logging
import json
import urllib.parse
from typing import List

# project
from . import Notifier, Event


class IftttNotifier(Notifier):
    def __init__(self, title_prefix: str, config: dict):
        logging.info("Initializing Ifttt notifier.")
        super().__init__(title_prefix, config)
        try:
            credentials = config["credentials"]
            self.token = credentials["api_token"]
            self.webhook_name = credentials["webhook_name"]
        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")

    def send_events_to_user(self, events: List[Event]) -> bool:
        errors = False
        for event in events:
            if event.type in self._notification_types and event.service in self._notification_services:
                conn = http.client.HTTPSConnection("maker.ifttt.com:443", timeout=self._conn_timeout_seconds)
                request_body = json.dumps({"Message": event.message, "Title": self.get_title_for_event(event)})
                conn.request(
                    "POST",
                    f"/trigger/{self.webhook_name}/json/with/key/{self.token}",
                    request_body,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "API-Key": f"{self.token}",
                    },
                )
                response = conn.getresponse()
                if response.getcode() != 200:
                    logging.warning(f"Problem sending event to user, code: {response.getcode()}")
                    errors = True
                conn.close()

        return not errors
