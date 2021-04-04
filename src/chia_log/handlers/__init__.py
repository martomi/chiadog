"""A LogHandler is a single responsibility
class that analyses a specific part of the log
stream and generates noteworthy events.

A single log handler could check for multiple
conditions. It delegates the task to ConditionCheckers.
"""

# std
from abc import ABC, abstractmethod
from typing import List

# project
from src.notifier import Event


class LogHandler(ABC):
    """Common interface for log handlers"""

    @abstractmethod
    def handle(self, logs: str) -> List[Event]:
        pass


class ConditionChecker(ABC):
    """Common interface for condition checkers"""

    @abstractmethod
    def check(self, obj: object) -> Event:
        pass
