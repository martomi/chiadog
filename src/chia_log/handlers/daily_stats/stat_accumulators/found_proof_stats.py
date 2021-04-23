# std
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
        self._found_proofs_total += obj.found_proofs_count

    def get_summary(self) -> str:
        return f"Proofs 🧾: {self._found_proofs_total} found"
