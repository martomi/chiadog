# std
import logging
from typing import List

# project
from src.notifier import Event
from . import LogHandler
from .condition_checkers import FinishedSignageConditionChecker
from .condition_checkers.non_skipped_signage_points import NonSkippedSignagePoints
from ..parsers.finished_signage_point_parser import FinishedSignagePointParser


class FinishedSignagePointHandler(LogHandler):
    """This handler parses all logs indicating finished signage point
    activity by the full node. It holds a list of condition checkers
    that are evaluated for each event.
    """

    def __init__(self):
        self._parser = FinishedSignagePointParser()
        self._cond_checkers: List[FinishedSignageConditionChecker] = [NonSkippedSignagePoints()]

    def handle(self, logs: str) -> List[Event]:
        """Process incoming logs, check all conditions
        and return a list of notable events.
        """

        events = []
        signage_point_messages = self._parser.parse(logs)
        if len(signage_point_messages) > 0:
            # Currently not generating keep-alive events for the full node
            # based on the signage points because it's tightly coupled to
            # the eligible plots check from the harvester
            logging.debug(f"Parsed {len(signage_point_messages)} signage point messages")

        # Run messages through all condition checkers
        for msg in signage_point_messages:
            for checker in self._cond_checkers:
                event = checker.check(msg)
                if event:
                    events.append(event)

        return events
