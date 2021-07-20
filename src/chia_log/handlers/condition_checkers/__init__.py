# std
from typing import Optional
from abc import ABC, abstractmethod

# project
from src.notifier import Event
from ...parsers.finished_signage_point_parser import FinishedSignagePointMessage
from ...parsers.harvester_activity_parser import HarvesterActivityMessage
from ...parsers.partial_parser import PartialMessage
from ...parsers.block_parser import BlockMessage


class FinishedSignageConditionChecker(ABC):
    @abstractmethod
    def check(self, obj: FinishedSignagePointMessage) -> Optional[Event]:
        pass


class HarvesterConditionChecker(ABC):
    @abstractmethod
    def check(self, obj: HarvesterActivityMessage) -> Optional[Event]:
        pass


class PartialConditionChecker(ABC):
    @abstractmethod
    def check(self, obj: PartialMessage) -> Optional[Event]:
        pass


class BlockConditionChecker(ABC):
    @abstractmethod
    def check(self, obj: BlockMessage) -> Optional[Event]:
        pass
