# std
from abc import ABC, abstractmethod
from typing import List

# project
from ...parsers.finished_signage_point_parser import FinishedSignagePointMessage
from ...parsers.harvester_activity_parser import HarvesterActivityMessage


class StatReporter(ABC):
    @abstractmethod
    def consume_harvester_messages(self, objects: List[HarvesterActivityMessage]):
        pass

    @abstractmethod
    def consume_signage_point_messages(self, objects: List[FinishedSignagePointMessage]):
        pass

    @abstractmethod
    def report(self):
        pass


class FinishedSignageConsumer(ABC):
    @abstractmethod
    def consume(self, obj: FinishedSignagePointMessage):
        pass


class HarvesterActivityConsumer(ABC):
    @abstractmethod
    def consume(self, obj: HarvesterActivityMessage):
        pass


class StatAccumulator(ABC):
    @abstractmethod
    def get_summary(self) -> str:
        pass

    @abstractmethod
    def get_data(self) -> dict:
        pass

    @abstractmethod
    def reset(self):
        pass
