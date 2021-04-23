# std
import logging
from datetime import datetime
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
        self._last_skip_timestamp = None
        self._last_signage_point_timestamp = None
        self._last_signage_point = None

    def check(self, obj: FinishedSignagePointMessage) -> Optional[Event]:
        if self._last_signage_point is None:
            self._last_signage_point_timestamp = obj.timestamp
            self._last_signage_point = obj.signage_point
            return None

        event = None
        skipped = calculate_skipped_signage_points(
            self._last_signage_point_timestamp, self._last_signage_point, obj.timestamp, obj.signage_point
        )

        # To reduce notification spam, only send notifications for skips larger than 1
        # or for multiple individual skips within 1 hour
        if skipped == 1:
            logging.info(f"Detected {skipped} skipped signage point.")
            if self._last_skip_timestamp:
                minutes_since_last_skip = (datetime.now() - self._last_skip_timestamp).seconds // 60
                if minutes_since_last_skip > 60:
                    logging.info("No other skips in the last 60 minutes. Can be safely ignored.")
                else:
                    message = "Experiencing networking issues? Skipped 2+ signage points in the last hour."
                    logging.warning(message)
                    event = Event(
                        type=EventType.USER,
                        priority=EventPriority.NORMAL,
                        service=EventService.FULL_NODE,
                        message=message,
                    )

        if skipped >= 2:
            message = f"Experiencing networking issues? Skipped {skipped} signage points!"
            logging.warning(message)
            event = Event(
                type=EventType.USER,
                priority=EventPriority.NORMAL,
                service=EventService.FULL_NODE,
                message=message,
            )

        if skipped != 0:
            self._last_skip_timestamp = datetime.now()
        self._last_signage_point_timestamp = obj.timestamp
        self._last_signage_point = obj.signage_point
        return event
