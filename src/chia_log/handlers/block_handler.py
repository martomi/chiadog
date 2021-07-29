# std
import logging
from typing import List, Optional

# project
from . import LogHandler
from ..parsers.block_parser import BlockParser
from .condition_checkers import BlockConditionChecker
from .condition_checkers.found_blocks import FoundBlocks
from .daily_stats.stats_manager import StatsManager
from src.notifier import Event


class BlockHandler(LogHandler):
    """This handler parses all logs indicating found block
    activity by the full node. It holds a list of condition checkers
    that are evaluated for each event.
    """

    def __init__(self):
        self._parser = BlockParser()
        self._cond_checkers: List[BlockConditionChecker] = [FoundBlocks()]

    def handle(self, logs: str, stats_manager: Optional[StatsManager] = None) -> List[Event]:
        """Process incoming logs, check all conditions
        and return a list of notable events.
        """

        events = []
        activity_messages = self._parser.parse(logs)
        if stats_manager:
            stats_manager.consume_block_messages(activity_messages)

        if len(activity_messages) > 0:
            # Currently not generating keep-alive events for the full node
            logging.debug(f"Parsed {len(activity_messages)} block found messages")

        # Run messages through all condition checkers
        for msg in activity_messages:
            for checker in self._cond_checkers:
                event = checker.check(msg)
                if event:
                    events.append(event)

        return events
