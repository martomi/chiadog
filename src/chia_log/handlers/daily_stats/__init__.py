# std
from abc import ABC, abstractmethod

# project
from ...parsers.finished_signage_point_parser import FinishedSignagePointMessage
from ...parsers.harvester_activity_parser import HarvesterActivityMessage
from ...parsers.wallet_added_coin_parser import WalletAddedCoinMessage


class FinishedSignageConsumer(ABC):
    @abstractmethod
    def consume(self, obj: FinishedSignagePointMessage):
        pass


class HarvesterActivityConsumer(ABC):
    @abstractmethod
    def consume(self, obj: HarvesterActivityMessage):
        pass


class WalletAddedCoinConsumer(ABC):
    @abstractmethod
    def consume(self, obj: WalletAddedCoinMessage):
        pass


class StatAccumulator(ABC):
    @abstractmethod
    def get_summary(self) -> str:
        pass

    @abstractmethod
    def reset(self):
        pass
