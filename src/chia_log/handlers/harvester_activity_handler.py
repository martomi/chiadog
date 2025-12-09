# std
import logging
from typing import List, Optional

# project
from . import LogHandlerInterface
from ..parsers.harvester_activity_parser import HarvesterActivityParser
from .condition_checkers import HarvesterConditionChecker
from .condition_checkers.non_decreasing_plots import NonDecreasingPlots
from .condition_checkers.quick_plot_search_time import QuickPlotSearchTime
from .condition_checkers.time_since_last_farm_event import TimeSinceLastFarmEvent
from .daily_stats.stats_manager import StatsManager
from .wins_tracker import WinsTracker
from src.notifier import Event, EventService, EventType, EventPriority


class HarvesterActivityHandler(LogHandlerInterface):
    """This handler parses all logs indicating harvester
    activity and participation in challenges. It holds a list
    of condition checkers that are evaluated for each event to
    ensure that farming is going smoothly.
    """

    @staticmethod
    def config_name() -> str:
        return "harvester_activity_handler"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._parser = HarvesterActivityParser()
        self._cond_checkers: List[HarvesterConditionChecker] = [
            TimeSinceLastFarmEvent(),
            NonDecreasingPlots(),
            QuickPlotSearchTime(),
        ]
        self._wins_tracker: Optional[WinsTracker] = None

    def set_wins_tracker(self, wins_tracker: WinsTracker) -> None:
        """Set the wins tracker for recording found proofs."""
        self._wins_tracker = wins_tracker
        logging.info("Wins tracker enabled for harvester activity handler")

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
            
            # Record wins if tracker is enabled
            if self._wins_tracker and msg.found_proofs_count > 0:
                try:
                    self._wins_tracker.record_win(msg)
                except Exception as e:
                    logging.error(f"Failed to record win: {e}")

        return events
