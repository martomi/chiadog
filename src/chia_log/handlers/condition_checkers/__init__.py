# std
from typing import Optional
from abc import ABC, abstractmethod

# project
from src.notifier import Event
from ...parsers.finished_signage_point_parser import FinishedSignagePointMessage
from ...parsers.harvester_activity_parser import HarvesterActivityMessage


class FinishedSignageConditionChecker(ABC):
    @abstractmethod
    def check(self, obj: FinishedSignagePointMessage) -> Optional[Event]:
        pass


class HarvesterConditionChecker(ABC):
    @abstractmethod
    def check(self, obj: HarvesterActivityMessage) -> Optional[Event]:
        pass
