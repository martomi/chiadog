# std
import logging
from typing import List, Optional

# project
from . import LogHandler
from ..parsers.partial_parser import PartialParser
from .condition_checkers import PartialConditionChecker
from .condition_checkers.found_partials import FoundPartials
from .daily_stats.stats_manager import StatsManager
from src.notifier import Event, EventService, EventType, EventPriority


class PartialHandler(LogHandler):
    """This handler parses all logs indicating found partials
    activity by the full node. It holds a list of condition checkers
    that are evaluated for each event.
    """

    def __init__(self):
        self._parser = PartialParser()
        self._cond_checkers: List[PartialConditionChecker] = [FoundPartials()]

    def handle(self, logs: str, stats_manager: Optional[StatsManager] = None) -> List[Event]:
        """Process incoming logs, check all conditions
        and return a list of notable events.
        """

        events = []
        activity_messages = self._parser.parse(logs)
        if stats_manager:
            stats_manager.consume_partial_messages(activity_messages)
        
        # Create a keep-alive event if any logs indicating
        # activity have been successfully parsed
        if len(activity_messages) > 0:
            logging.debug(f"Parsed {len(activity_messages)} activity messages")
            events.append(
                Event(
                    type=EventType.KEEPALIVE, priority=EventPriority.NORMAL, service=EventService.FARMER, message=""
                )
            )

        # Run messages through all condition checkers
        for msg in activity_messages:
            for checker in self._cond_checkers:
                event = checker.check(msg)
                if event:
                    events.append(event)

        return events
