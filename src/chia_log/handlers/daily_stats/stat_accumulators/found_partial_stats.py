# std
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
        self._found_partials_total += obj.partials_count

    def get_summary(self) -> str:
        return f"\t - {self._found_partials_total} partials submitted 📑"
