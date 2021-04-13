# std
import logging
import os
import subprocess
from typing import List

# project
from . import Notifier, Event, EventType


class ScriptNotifier(Notifier):
    def __init__(self, title_prefix: str, config: dict):
        logging.info("Initializing script notifier.")
        super().__init__(title_prefix, config)
        try:
            self.script_path = config["script_path"]
        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")
        if self.script_path:
            if os.path.isfile(self.script_path):
                if os.access(self.script_path, os.X_OK) is False:
                    logging.error(f"Invalid script path. File is not executable: {self.script_path}")
            else:
                logging.error(f"Invalid script path. File does not exist: {self.script_path}")
                self.script_path = None

    def send_events_to_user(self, events: List[Event]) -> bool:
        errors = False

        if self.script_path is None:
            errors = True

        if errors is False:
            for event in events:
                if event.type == EventType.USER:
                    subprocess.run([str(self.script_path), event.priority.name, event.service.name, event.message])

        return errors
