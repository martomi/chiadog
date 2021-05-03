# std
from datetime import datetime

# project
from .. import WalletAddedCoinMessage, WalletAddedCoinConsumer, StatAccumulator


class WalletAddedCoinStats(WalletAddedCoinConsumer, StatAccumulator):
    def __init__(self):
        self._last_reset_time = datetime.now()
        self._total_added_mojos = 0

    def reset(self):
        self._last_reset_time = datetime.now()
        self._total_added_mojos = 0

    def consume(self, obj: WalletAddedCoinMessage):
        self._total_added_mojos += obj.amount_mojos

    def get_summary(self) -> str:
        return f"Received ☘️: {(self._total_added_mojos / 1e12):0.2f} XCH"
