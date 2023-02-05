# std
from datetime import datetime

# project
from .. import HarvesterActivityConsumer, HarvesterActivityMessage, StatAccumulator


class SearchTimeStats(HarvesterActivityConsumer, StatAccumulator):
    def __init__(self):
        self._last_reset_time = datetime.now()
        self._num_measurements = 0
        self._avg_time_seconds = 0.0
        self._over_5_seconds = 0
        self._over_15_seconds = 0

    def reset(self):
        self._last_reset_time = datetime.now()
        self._num_measurements = 0
        self._avg_time_seconds = 0.0
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
        pct_over_5seconds: float = 0
        pct_over_15seconds: float = 0

        if self._num_measurements > 0:
            pct_over_5seconds = self._over_5_seconds / self._num_measurements * 100
            pct_over_15seconds = self._over_15_seconds / self._num_measurements * 100

        return (
            f"Search 🔍: \n"
            f"\t - average: {self._avg_time_seconds:0.2f}s over {self._num_measurements} searches\n"
            f"\t - over 5s: {self._over_5_seconds} occasions ({pct_over_5seconds:0.1f}%)\n"
            f"\t - over 15s: {self._over_15_seconds} occasions ({pct_over_15seconds:0.1f}%)"
        )
