# std
from datetime import datetime

# project
from .. import HarvesterActivityConsumer, HarvesterActivityMessage, StatAccumulator


class EligiblePlotsStats(HarvesterActivityConsumer, StatAccumulator):
    def __init__(self):
        self._last_reset_time = datetime.now()
        self._eligible_plots_total = 0
        self._eligible_events_total = 0

    def reset(self):
        self._last_reset_time = datetime.now()
        self._eligible_plots_total = 0
        self._eligible_events_total = 0

    def consume(self, obj: HarvesterActivityMessage):
        self._eligible_plots_total += obj.eligible_plots_count
        self._eligible_events_total += 1

    def get_summary(self) -> str:
        return f"Eligible plots 🥇: {self._eligible_plots_total / self._eligible_events_total:0.2f} average"
