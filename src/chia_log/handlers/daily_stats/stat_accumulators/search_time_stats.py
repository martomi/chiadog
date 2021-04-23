# std
from datetime import datetime

# project
from .. import HarvesterActivityConsumer, HarvesterActivityMessage, StatAccumulator


class SearchTimeStats(HarvesterActivityConsumer, StatAccumulator):
    def __init__(self):
        self._last_reset_time = datetime.now()
        self._num_measurements = 0
        self._max_time_seconds = 0
        self._avg_time_seconds = 0

    def reset(self):
        self._last_reset_time = datetime.now()
        self._num_measurements = 0
        self._max_time_seconds = 0
        self._avg_time_seconds = 0

    def consume(self, obj: HarvesterActivityMessage):
        self._num_measurements += 1
        self._max_time_seconds = max(self._max_time_seconds, obj.search_time_seconds)
        self._avg_time_seconds += (obj.search_time_seconds - self._avg_time_seconds) / self._num_measurements

    def get_summary(self) -> str:
        return f"Search 🔍: {self._avg_time_seconds:0.2f}s average, {self._max_time_seconds:0.2f}s max"
