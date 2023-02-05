# std
from datetime import datetime

# project
from src.chia_log.handlers.util.calculate_skipped_signage_points import calculate_skipped_signage_points
from .. import FinishedSignagePointMessage, FinishedSignageConsumer, StatAccumulator


class SignagePointStats(FinishedSignageConsumer, StatAccumulator):
    def __init__(self):
        self._last_reset_time = datetime.now()
        self._last_signage_point_timestamp: datetime = datetime.fromtimestamp(0)
        self._last_signage_point: int = 0
        self._skips_total = 0
        self._total = 0

    def reset(self):
        self._last_reset_time = datetime.now()
        self._skips_total = 0
        self._total = 0

    def consume(self, obj: FinishedSignagePointMessage):
        if self._last_signage_point == 0:
            self._last_signage_point_timestamp = obj.timestamp
            self._last_signage_point = obj.signage_point
            return

        valid, skips = calculate_skipped_signage_points(
            self._last_signage_point_timestamp,
            self._last_signage_point,
            obj.timestamp,
            obj.signage_point,
        )

        if not valid:
            return

        self._skips_total += skips
        self._total += 1 + skips

        self._last_signage_point_timestamp = obj.timestamp
        self._last_signage_point = obj.signage_point

    def get_summary(self) -> str:
        if self._total == 0:
            return "Skipped SPs ⚠️: Unknown"
        if self._skips_total > 0:
            percentage_skipped = (self._skips_total / self._total) * 100
            return f"Skipped SPs ⚠️: {self._skips_total} ({percentage_skipped:0.2f}%)"
        return "Skipped SPs ✅️: None"
