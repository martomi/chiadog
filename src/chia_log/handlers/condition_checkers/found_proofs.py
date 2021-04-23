# std
import logging
from typing import Optional

# project
from src.notifier import Event, EventService, EventType, EventPriority
from . import HarvesterConditionChecker
from ...parsers.harvester_activity_parser import HarvesterActivityMessage


class FoundProofs(HarvesterConditionChecker):
    """Check if any proofs were found."""

    def __init__(self):
        logging.info("Enabled check for found proofs.")

    def check(self, obj: HarvesterActivityMessage) -> Optional[Event]:
        if obj.found_proofs_count > 0:
            message = f"Found {obj.found_proofs_count} proof(s)!"
            logging.info(message)
            return Event(
                type=EventType.USER, priority=EventPriority.LOW, service=EventService.HARVESTER, message=message
            )

        return None
