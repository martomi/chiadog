# std
import http.client
import logging
import json
import urllib.parse
from typing import List

# project
from . import Notifier, Event, EventType


class SlackNotifier(Notifier):
    def __init__(self, title_prefix: str, config: dict):
        logging.info("Initializing Slack notifier.")
        super().__init__(title_prefix, config)
        try:
            self.webhook_url = config["webhook_url"]
        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")

    def send_events_to_user(self, events: List[Event]) -> bool:
        errors = False
        for event in events:
            if event.type == EventType.USER:
                request_body = json.dumps(
                    {
                        "text": f"*{self.get_title_for_event(event)}*\n{event.message}",
                    }
                )

                o = urllib.parse.urlparse(self.webhook_url)
                conn = http.client.HTTPSConnection(o.netloc)
                conn.request(
                    "POST",
                    o.path,
                    request_body,
                    {"Content-type": "application/json"},
                )
                response = conn.getresponse()
                if response.getcode() != 200:
                    logging.warning(f"Problem sending event to user, code: {response.getcode()}")
                    errors = True
                conn.close()

        return errors
