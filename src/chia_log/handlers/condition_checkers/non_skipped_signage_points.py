# std
import logging
from typing import Optional

# project
from . import FinishedSignageConditionChecker
from src.notifier import Event, EventService, EventType, EventPriority
from src.chia_log.parsers.finished_signage_point_parser import FinishedSignagePointMessage
from src.chia_log.handlers.util.calculate_skipped_signage_points import calculate_skipped_signage_points


class NonSkippedSignagePoints(FinishedSignageConditionChecker):
    """Check that the full node did not skip any signage points.
    If there are signage points missing, this could indicate connection
    issues which prevent the farmer from participating in all challenges.
    """

    def __init__(self):
        logging.info("Enabled check for finished signage points.")
        self._last_signage_point_timestamp = None
        self._last_signage_point = None
        self._roll_over_point = 64

    def check(self, obj: FinishedSignagePointMessage) -> Optional[Event]:
        if self._last_signage_point is None:
            self._last_signage_point_timestamp = obj.timestamp
            self._last_signage_point = obj.signage_point
            return None

        event = None
        skipped = calculate_skipped_signage_points(
            self._last_signage_point_timestamp, self._last_signage_point, obj.timestamp, obj.signage_point
        )

        if skipped > 1:
            message = (
                f"Experiencing networking issues? Skipped {skipped} signage points! "
                f"Last {self._last_signage_point}/64, current {obj.signage_point}/64."
            )
            logging.warning(message)
            event = Event(
                type=EventType.USER, priority=EventPriority.NORMAL, service=EventService.FULL_NODE, message=message
            )

        self._last_signage_point_timestamp = obj.timestamp
        self._last_signage_point = obj.signage_point
        return event
