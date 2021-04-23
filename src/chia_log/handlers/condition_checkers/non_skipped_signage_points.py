# std
import logging
from typing import Optional

# project
from . import FinishedSignageConditionChecker
from src.notifier import Event, EventService, EventType, EventPriority
from src.chia_log.parsers.finished_signage_point_parser import FinishedSignagePointMessage


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
        time_diff_seconds = (obj.timestamp - self._last_signage_point_timestamp).seconds
        increment_diff = obj.signage_point - (self._last_signage_point % self._roll_over_point)

        if increment_diff <= 0 or increment_diff > 1:
            # This is hacky addition to prevent false alarms for some network-wide issues that
            # aren't necessarily related to the local node. See "testNetworkScramble" test case.
            # Signage points are expected approx every 8-10 seconds. If a point was skipped for real
            # then we expect the time difference to be at least 2*8 seconds. Otherwise it's flaky event.
            if time_diff_seconds < 15:
                logging.info(
                    f"Detected unusual network activity. Last signage point {self._last_signage_point}, "
                    f"current signage point {obj.signage_point}. Time difference: {time_diff_seconds} "
                    f"seconds. Seems unrelated to the local node. Ignoring..."
                )
            else:
                message = (
                    f"Experiencing networking issues? Skipped some signage points! "
                    f"Last {self._last_signage_point}/64, current {obj.signage_point}/64."
                )
                logging.warning(message)
                event = Event(
                    type=EventType.USER, priority=EventPriority.NORMAL, service=EventService.FULL_NODE, message=message
                )

        self._last_signage_point_timestamp = obj.timestamp
        self._last_signage_point = obj.signage_point
        return event
