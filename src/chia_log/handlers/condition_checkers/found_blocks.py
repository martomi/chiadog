# std
import logging
from typing import Optional

# project
from src.notifier import Event, EventService, EventType, EventPriority
from . import FarmingConditionChecker
from ...parsers.farming_parser import FarmingMessage


class FoundBlocks(FarmingConditionChecker):
    """Check if any blocks were found."""

    def __init__(self):
        logging.info("Enabled check for found block.")

    def check(self, obj: FarmingMessage) -> Optional[Event]:
        if obj.found_blocks_count > 0:
            message = f"Block found!!"
            logging.info(message)
            return Event(
                type=EventType.USER, priority=EventPriority.HIGH, service=EventService.FULL_NODE, message=message
            )

        return None
