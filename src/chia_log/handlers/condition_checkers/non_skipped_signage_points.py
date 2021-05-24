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

    def check(self, obj: FinishedSignagePointMessage) -> Optional[Event]:
        if self._last_signage_point is None:
            self._last_signage_point_timestamp = obj.timestamp
            self._last_signage_point = obj.signage_point
            return None

        event = None
        valid, skipped = calculate_skipped_signage_points(
            self._last_signage_point_timestamp, self._last_signage_point, obj.timestamp, obj.signage_point
        )

        if not valid:
            return None

        # To reduce notification spam, only send notifications for skips larger than 1
        if skipped == 1:
            logging.info(
                f"Detected {skipped} skipped signage point."
                "This is expected to happen occasionally and not a reason for concern."
            )
        elif skipped >= 2:
            message = f"Experiencing networking issues? Skipped {skipped} signage points! " "More info: git.io/Js5B1"
            logging.warning(message)
            event = Event(
                type=EventType.USER,
                priority=EventPriority.NORMAL,
                service=EventService.FULL_NODE,
                message=message,
            )

        self._last_signage_point_timestamp = obj.timestamp
        self._last_signage_point = obj.signage_point
        return event
