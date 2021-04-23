# std
import logging
from typing import Optional

# project
from src.notifier import Event, EventService, EventType, EventPriority
from . import HarvesterConditionChecker
from ...parsers.harvester_activity_parser import HarvesterActivityMessage


class QuickPlotSearchTime(HarvesterConditionChecker):
    """Farming challenges need to be responded in 30 or less
    seconds. Ensure that HDD seek time for plots is quick
    enough that this condition is always satisfied
    """

    def __init__(self):
        logging.info("Enabled check for time taken to respond to challenges.")
        self._warning_threshold = 20  # seconds

    def check(self, obj: HarvesterActivityMessage) -> Optional[Event]:
        if obj.search_time_seconds > self._warning_threshold:
            message = f"Seeking plots took too long: {obj.search_time_seconds} seconds!"
            logging.warning(message)
            return Event(
                type=EventType.USER, priority=EventPriority.NORMAL, service=EventService.HARVESTER, message=message
            )

        return None
