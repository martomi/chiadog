# std
import logging
from datetime import datetime

# project
from .. import HarvesterActivityConsumer, HarvesterActivityMessage, StatAccumulator


class FoundProofStats(HarvesterActivityConsumer, StatAccumulator):
    def __init__(self):
        self._last_reset_time = datetime.now()
        self._found_proofs_total = 0

    def reset(self):
        self._last_reset_time = datetime.now()
        self._found_proofs_total = 0

    def consume(self, obj: HarvesterActivityMessage):
        if obj.found_proofs_count > 0:
            logging.info("Found a proof!")
        self._found_proofs_total += obj.found_proofs_count

    def get_summary(self) -> str:
        if self._found_proofs_total == 0:
            return "Proofs 🧾: None"
        return f"Proofs 🧾: {self._found_proofs_total} found!"
