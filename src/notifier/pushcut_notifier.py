# std
import http.client
import logging
import json
import urllib.parse
from typing import List

# project
from . import Notifier, Event


class PushcutNotifier(Notifier):
    def __init__(self, title_prefix: str, config: dict):
        logging.info("Initializing PushCut notifier.")
        super().__init__(title_prefix, config)
        try:
            credentials = config["credentials"]
            self.token = credentials["api_token"]
            self.notification_name = credentials["notification_name"]
        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")

    def send_events_to_user(self, events: List[Event]) -> bool:
        errors = False
        for event in events:
            if event.type in self._notification_types and event.service in self._notification_services:
                conn = http.client.HTTPSConnection("api.pushcut.io:443", timeout=self._conn_timeout_seconds)
                request_body = json.dumps({"text": event.message, "title": self.get_title_for_event(event)})
                conn.request(
                    "POST",
                    f"/v1/notifications/{self.notification_name}",
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
