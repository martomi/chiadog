# std
import logging
from typing import List, Optional

# project
from . import LogHandler
from ..parsers.harvester_activity_parser import HarvesterActivityParser
from .condition_checkers import HarvesterConditionChecker
from .condition_checkers.non_decreasing_plots import NonDecreasingPlots
from .condition_checkers.quick_plot_search_time import QuickPlotSearchTime
from .condition_checkers.time_since_last_farm_event import TimeSinceLastFarmEvent
from .daily_stats.stats_manager import StatsManager
from src.notifier import Event, EventService, EventType, EventPriority


class HarvesterActivityHandler(LogHandler):
    """This handler parses all logs indicating harvester
    activity and participation in challenges. It holds a list
    of condition checkers that are evaluated for each event to
    ensure that farming is going smoothly.
    """

    def __init__(self):
        self._parser = HarvesterActivityParser()
        self._cond_checkers: List[HarvesterConditionChecker] = [
            TimeSinceLastFarmEvent(),
            NonDecreasingPlots(),
            QuickPlotSearchTime(),
        ]

    def handle(self, logs: str, stats_manager: Optional[StatsManager] = None) -> List[Event]:
        """Process incoming logs, check all conditions
        and return a list of notable events.
        """

        events = []
        activity_messages = self._parser.parse(logs)
        if stats_manager:
            stats_manager.consume_harvester_messages(activity_messages)

        # Create a keep-alive event if any logs indicating
        # activity have been successfully parsed
        if len(activity_messages) > 0:
            logging.debug(f"Parsed {len(activity_messages)} activity messages")
            events.append(
                Event(
                    type=EventType.KEEPALIVE, priority=EventPriority.NORMAL, service=EventService.HARVESTER, message=""
                )
            )

        # Run messages through all condition checkers
        for msg in activity_messages:
            for checker in self._cond_checkers:
                event = checker.check(msg)
                if event:
                    events.append(event)

        return events
