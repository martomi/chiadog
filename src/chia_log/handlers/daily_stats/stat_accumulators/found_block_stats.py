# std
import logging
from datetime import datetime

# project
from .. import BlockConsumer, BlockMessage, StatAccumulator


class FoundBlockStats(PartialConsumer, StatAccumulator):
    def __init__(self):
        self._last_reset_time = datetime.now()
        self._found_blocks_total = 0

    def reset(self):
        self._last_reset_time = datetime.now()
        self._found_blocks_total = 0

    def consume(self, obj: BlockMessage):
        if obj.blocks_count > 0:
            logging.info("Found a block!")
        self._found_blocks_total += obj.blocks_count

    def get_summary(self) -> str:
        if self._found_blocks_total == 0:
            return "Blocks 📦: None"
        return f"Blocks 📦: {self._found_blocks_total} found!"
