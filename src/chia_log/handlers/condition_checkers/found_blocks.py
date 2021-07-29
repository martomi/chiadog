# std
import logging
from typing import Optional

# project
from src.notifier import Event, EventService, EventType, EventPriority
from . import BlockConditionChecker
from ...parsers.block_parser import BlockMessage


class FoundBlocks(BlockConditionChecker):
    """Check if any blocks were found."""

    def __init__(self):
        logging.info("Enabled check for found blocks.")

    def check(self, obj: BlockMessage) -> Optional[Event]:
        if obj.blocks_count > 0:
            message = "Block found!"
            logging.info(message)
            return Event(
                type=EventType.USER, priority=EventPriority.LOW, service=EventService.FULL_NODE, message=message
            )

        return None
