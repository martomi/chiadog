# std
import logging
from typing import Optional

# project
from src.notifier import Event, EventService, EventType, EventPriority
from . import HarvesterConditionChecker
from ...parsers.harvester_activity_parser import HarvesterActivityMessage


class NonDecreasingPlots(HarvesterConditionChecker):
    """The total number of farmed plots is not expected
    to decrease. Decreasing number of plots may be a sign
    of unstable USB connection for external HDDs.
    """

    def __init__(self):
        logging.info("Enabled check for non-decreasing total plot count.")
        self._max_farmed_plots = 0

    def check(self, obj: HarvesterActivityMessage) -> Optional[Event]:
        if obj.total_plots_count > self._max_farmed_plots:
            logging.info(f"Detected new plots. Farming with {obj.total_plots_count} plots.")
            self._max_farmed_plots = obj.total_plots_count

        event = None
        if obj.total_plots_count < self._max_farmed_plots:
            message = (
                f"Disconnected HDD? The total plot count decreased from "
                f"{self._max_farmed_plots} to {obj.total_plots_count}."
            )
            logging.warning(message)
            event = Event(
                type=EventType.USER, priority=EventPriority.HIGH, service=EventService.HARVESTER, message=message
            )

        # Update max plots to prevent repeated alarms
        self._max_farmed_plots = obj.total_plots_count

        return event
