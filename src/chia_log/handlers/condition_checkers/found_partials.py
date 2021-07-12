# std
import logging
from typing import Optional

# project
from src.notifier import Event, EventService, EventType, EventPriority
from . import PartialConditionChecker
from ...parsers.partial_parser import PartialMessage


class FoundPartials(PartialConditionChecker):
    """Check if any partials were found."""

    def __init__(self):
        logging.info("Enabled check for found partials.")

    def check(self, obj: PartialMessage) -> Optional[Event]:
        if obj.partials_count > 0:
            message = f"Submitting partials"
            logging.info(message)
            return Event(
                type=EventType.USER, priority=EventPriority.LOW, service=EventService.FARMER, message=message
            )

        return None
