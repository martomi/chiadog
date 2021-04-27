# std
import logging
from typing import Optional

# project
from src.notifier import Event, EventService, EventType, EventPriority
from . import HarvesterConditionChecker
from ...parsers.harvester_activity_parser import HarvesterActivityMessage


class TimeSinceLastFarmEvent(HarvesterConditionChecker):
    """Check that elapsed time since last eligible farming event was
    inline with expectations. Usually every < 10 seconds.

    If this check fails, this might be indication of unstable connection.
    This is non-high priority because triggering the event means that
    the farmer already recovered. If the farming completely stops it will
    be caught by the keep-alive check which generates a high priority event.
    """

    def __init__(self):
        logging.info("Enabled check for farming events.")
        self._info_threshold = 30
        self._warning_threshold = 60
        self._last_timestamp = None

    def check(self, obj: HarvesterActivityMessage) -> Optional[Event]:
        if self._last_timestamp is None:
            self._last_timestamp = obj.timestamp
            return None

        event = None
        seconds_since_last = (obj.timestamp - self._last_timestamp).seconds

        if seconds_since_last > self._warning_threshold:
            message = (
                f"Experiencing networking issues? Harvester did not participate in any challenge "
                f"for {seconds_since_last} seconds. It's now working again."
            )
            logging.warning(message)
            event = Event(
                type=EventType.USER, priority=EventPriority.NORMAL, service=EventService.HARVESTER, message=message
            )
        elif seconds_since_last > self._info_threshold:
            # This threshold seems to be surpassed multiple times per day
            # on the current network. So it only generates an INFO log.
            logging.info(f"Last farming event was {seconds_since_last} seconds ago. This is unusual.")

        self._last_timestamp = obj.timestamp
        return event
