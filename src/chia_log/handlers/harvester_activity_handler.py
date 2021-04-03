# std
import logging
from typing import List, Optional

# project
from src.notifier import Event, EventService, EventType, EventPriority
from . import LogHandler, ConditionChecker
from ..parsers.harvester_activity_parser import HarvesterActivityParser, HarvesterActivityMessage


class HarvesterActivityHandler(LogHandler):
    """This handler parses all logs indicating harvester
    activity and participation in challenges. It holds a list
    of condition checkers that are evaluated for each event to
    ensure that farming is going smoothly.
    """

    def __init__(self):
        self._parser = HarvesterActivityParser()
        self._cond_checkers = [
            TimeSinceLastFarmEvent(),
            NonDecreasingPlots(),
            QuickPlotSearchTime(),
            FoundProofs()
        ]

    def handle(self, logs: str) -> List[Event]:
        """Process incoming logs, check all conditions
        and return a list of notable events.
        """

        events = []
        activity_messages = self._parser.parse(logs)

        # Create a keep-alive event if any logs indicating
        # activity have been successfully parsed
        if len(activity_messages) > 0:
            logging.debug(f"Parsed {len(activity_messages)} activity messages")
            events.append(Event(
                type=EventType.KEEPALIVE,
                priority=EventPriority.NORMAL,
                service=EventService.HARVESTER,
                message=""
            ))

        # Run messages through all condition checkers
        for msg in activity_messages:
            for checker in self._cond_checkers:
                event = checker.check(msg)
                if event:
                    events.append(event)

        return events


class TimeSinceLastFarmEvent(ConditionChecker):
    """Check that elapsed time since last eligible farming event was
    inline with expectations. Usually every < 10 seconds.

    If this check fails, this might be indication of unstable connection.
    This is non-high priority because triggering the event means that
    the farmer already recovered. If the farming completely stops it will
    be caught by the keep-alive check which generates a high priority event.
    """

    def __init__(self):
        self._warning_threshold = 30
        self._last_timestamp = None

    def check(self, obj: HarvesterActivityMessage) -> Optional[Event]:
        if self._last_timestamp is None:
            self._last_timestamp = obj.timestamp
            return None

        event = None
        seconds_since_last = (obj.timestamp - self._last_timestamp).seconds

        if seconds_since_last > self._warning_threshold:
            message = f"Harvester did not participate in any challenge for {seconds_since_last} seconds. " \
                      f"This might indicate networking issues. It's now working again."
            logging.warning(message)
            event = Event(
                type=EventType.USER,
                priority=EventPriority.NORMAL,
                service=EventService.HARVESTER,
                message=message
            )

        self._last_timestamp = obj.timestamp
        return event


class NonDecreasingPlots(ConditionChecker):
    """The total number of farmed plots is not expected
    to decrease. Decreasing number of plots may be a sign
    of unstable USB connection for external HDDs.
    """

    def __init__(self):
        self._max_farmed_plots = 0

    def check(self, obj: HarvesterActivityMessage) -> Optional[Event]:
        if obj.total_plots_count > self._max_farmed_plots:
            logging.info(f"Detected new plots. Farming with {obj.total_plots_count} plots.")
            self._max_farmed_plots = obj.total_plots_count

        event = None
        if obj.total_plots_count < self._max_farmed_plots:
            message = f"The total plot count decreased from {self._max_farmed_plots} to {obj.total_plots_count}."
            logging.warning(message)
            event = Event(
                type=EventType.USER,
                priority=EventPriority.HIGH,
                service=EventService.HARVESTER,
                message=message
            )

        # Update max plots to prevent repeated alarms
        self._max_farmed_plots = obj.total_plots_count

        return event


class QuickPlotSearchTime(ConditionChecker):
    """Farming challenges need to be responded in 30 or less
    seconds. Ensure that HDD seek time for plots is quick
    enough that this condition is always satisfied
    """

    def __init__(self):
        self._warning_threshold = 25  # seconds

    def check(self, obj: HarvesterActivityMessage) -> Optional[Event]:
        if obj.search_time_seconds > self._warning_threshold:
            message = f"Seeking plots took too long: {obj.search_time_seconds} seconds!"
            logging.warning(message)
            return Event(
                type=EventType.USER,
                priority=EventPriority.NORMAL,
                service=EventService.HARVESTER,
                message=message
            )

        return None


class FoundProofs(ConditionChecker):
    """Check if any proofs were found."""

    def check(self, obj: HarvesterActivityMessage) -> Optional[Event]:
        if obj.found_proofs_count > 0:
            message = f"Found {obj.found_proofs_count} proofs!"
            logging.info(message)
            return Event(
                type=EventType.USER,
                priority=EventPriority.LOW,
                service=EventService.HARVESTER,
                message=message
            )

        return None
