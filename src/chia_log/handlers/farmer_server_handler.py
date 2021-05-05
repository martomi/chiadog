# std
import logging
from typing import List, Optional

# project
from . import LogHandler
from ..parsers.farmer_server_parser import FarmerServerParser
from .condition_checkers import FarmerConditionChecker
from .condition_checkers.remote_harvester_activity import RemoteHarvesterActivity
from .daily_stats.stats_manager import StatsManager
from src.notifier import Event, EventService, EventType, EventPriority


class FarmerServerHandler(LogHandler):
    """This handler parses all logs indicating farmer_server
    activity and participation of remote harvester in challenges.
    It holds a list of condition checkers that are evaluated for
    each event to ensure that farming is going smoothly.
    """

    def __init__(self):
        self._parser = FarmerServerParser()
        self._cond_checkers: List[FarmerConditionChecker] = [
            RemoteHarvesterActivity(),
        ]

    def handle(self, logs: str, stats_manager: Optional[StatsManager] = None) -> List[Event]:
        """Process incoming logs, check all conditions
        and return a list of notable events.
        """

        events = []
        activity_messages = self._parser.parse(logs)
        # if stats_manager:
        #     stats_manager.consume_farmer_messages(activity_messages)

        # Create a keep-alive event if any logs indicating
        # activity have been successfully parsed
        if len(activity_messages) > 0:
            logging.debug(f"Parsed {len(activity_messages)} farmer_server messages")

        # Run messages through all condition checkers
        for msg in activity_messages:
            for checker in self._cond_checkers:
                event = checker.check(msg)
                if event:
                    events.append(event)

        return events
