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
        # When copying plots it's common that plots decrease by 1 temporarily
        # by setting the default threshold to 2, we can avoid false alarms
        self._decrease_warn_threshold = 2
        self._increase_info_threshold = 2

    def check(self, obj: HarvesterActivityMessage) -> Optional[Event]:
        event = None
        if obj.total_plots_count > self._max_farmed_plots:
            logging.info(f"Detected new plots. Farming with {obj.total_plots_count} plots.")
            message = (
                f"Connected HDD? The total plot count increased from "
                f"{self._max_farmed_plots} to {obj.total_plots_count}."
            )
            logging.info(message)

            if obj.total_plots_count - self._max_farmed_plots > self._increase_info_threshold:
                event = Event(
                    type=EventType.PLOTINCREASE,
                    priority=EventPriority.LOW,
                    service=EventService.HARVESTER,
                    message=message,
                )

            self._max_farmed_plots = obj.total_plots_count

        if obj.total_plots_count < self._max_farmed_plots:
            if self._max_farmed_plots - obj.total_plots_count < self._decrease_warn_threshold:
                logging.info(
                    f"Plots decreased from {self._max_farmed_plots} to {obj.total_plots_count}. "
                    f"This is ignored because it's below threshold of {self._decrease_warn_threshold}"
                )
            else:
                message = (
                    f"Disconnected HDD? The total plot count decreased from "
                    f"{self._max_farmed_plots} to {obj.total_plots_count}."
                )
                logging.warning(message)
                event = Event(
                    type=EventType.PLOTDECREASE,
                    priority=EventPriority.HIGH,
                    service=EventService.HARVESTER,
                    message=message,
                )

        # Update max plots to prevent repeated alarms
        self._max_farmed_plots = obj.total_plots_count

        return event
