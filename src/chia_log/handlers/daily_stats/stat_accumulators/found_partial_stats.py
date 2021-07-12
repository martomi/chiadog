# std
import logging
from datetime import datetime

# project
from .. import PartialConsumer, PartialMessage, StatAccumulator


class FoundPartialStats(PartialConsumer, StatAccumulator):
    def __init__(self):
        self._last_reset_time = datetime.now()
        self._found_partials_total = 0

    def reset(self):
        self._last_reset_time = datetime.now()
        self._found_partials_total = 0

    def consume(self, obj: PartialMessage):
        if obj.partials_count > 0:
            logging.info("Submitting a partial!")
        self._found_partials_total += obj.partials_count

    def get_summary(self) -> str:
        if self._found_partials_total == 0:
            return "Partials submitted 🧾: None"
        return f"Partials submitted 🧾: {self._found_partials_total}!"
