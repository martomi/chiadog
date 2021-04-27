# std
from datetime import datetime

# project
from src.chia_log.handlers.util.calculate_skipped_signage_points import calculate_skipped_signage_points
from .. import FinishedSignagePointMessage, FinishedSignageConsumer, StatAccumulator


class SignagePointStats(FinishedSignageConsumer, StatAccumulator):
    def __init__(self):
        self._last_reset_time = datetime.now()
        self._last_signage_point_timestamp = None
        self._last_signage_point = None
        self._skips_total = 0
        self._total = 0

    def reset(self):
        self._last_reset_time = datetime.now()
        self._skips_total = 0

    def consume(self, obj: FinishedSignagePointMessage):
        if self._last_signage_point is None:
            self._last_signage_point_timestamp = obj.timestamp
            self._last_signage_point = obj.signage_point
            return

        skips = calculate_skipped_signage_points(
            self._last_signage_point_timestamp, self._last_signage_point, obj.timestamp, obj.signage_point
        )
        self._skips_total += skips
        self._total += 1

        self._last_signage_point_timestamp = obj.timestamp
        self._last_signage_point = obj.signage_point

    def get_summary(self) -> str:
        percentage_skipped = (self._skips_total / self._total) * 100
        if self._skips_total > 0:
            return f"Skipped SPs ⚠️: {self._skips_total} ({percentage_skipped:0.2f}%)"
        return "Skipped SPs ✅️: None"
