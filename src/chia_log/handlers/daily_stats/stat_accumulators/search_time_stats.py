# std
from datetime import datetime

# project
from .. import HarvesterActivityConsumer, HarvesterActivityMessage, StatAccumulator


class SearchTimeStats(HarvesterActivityConsumer, StatAccumulator):
    def __init__(self):
        self._last_reset_time = datetime.now()
        self._num_measurements = 0
        self._avg_time_seconds = 0
        self._over_5_seconds = 0
        self._over_15_seconds = 0

    def reset(self):
        self._last_reset_time = datetime.now()
        self._num_measurements = 0
        self._avg_time_seconds = 0
        self._over_5_seconds = 0
        self._over_15_seconds = 0

    def consume(self, obj: HarvesterActivityMessage):
        self._num_measurements += 1
        self._avg_time_seconds += (obj.search_time_seconds - self._avg_time_seconds) / self._num_measurements
        if obj.search_time_seconds > 5:
            self._over_5_seconds += 1
        if obj.search_time_seconds > 15:
            self._over_15_seconds += 1

    def get_summary(self) -> str:
        return (
            f"Search 🔍: \n"
            f"\t - average: {self._avg_time_seconds:0.2f}s average\n"
            f"\t - over 5s: {self._over_5_seconds} occasions\n"
            f"\t - over 15s: {self._over_15_seconds} occasions"
        )
