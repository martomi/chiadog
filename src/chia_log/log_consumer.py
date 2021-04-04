"""Log consumers are responsible for fetching chia logs
and propagating them to subscribers for further handling.

This abstraction should provide an easy ability to switch between
local file reader and fetching logs from a remote machine.
The latter has not been implemented yet. Feel free to add it.
"""

# std
import logging
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from threading import Thread
from typing import List


class LogConsumerSubscriber(ABC):
    """Interface for log consumer subscribers (i.e. handlers)"""

    @abstractmethod
    def consume_logs(self, logs: str):
        """This method will be called when new logs are available"""
        pass


class LogConsumer(ABC):
    """Abstract class providing common interface for log consumers"""

    def __init__(self):
        self._subscribers: List[LogConsumerSubscriber] = []

    @abstractmethod
    def stop(self):
        pass

    def subscribe(self, subscriber: LogConsumerSubscriber):
        self._subscribers.append(subscriber)

    def _notify_subscribers(self, logs: str):
        for subscriber in self._subscribers:
            subscriber.consume_logs(logs)


class FileLogConsumer(LogConsumer):
    """Specific implementation for a simple file consumer"""

    def __init__(self, log_path: Path):
        super().__init__()
        self._log_path = log_path
        self._is_running = True
        self._thread = Thread(target=self._consume_loop)
        self._thread.start()

    def stop(self):
        logging.info("Stopping")
        self._is_running = False

    def _consume_loop(self):
        expanded_user_log_path = self._log_path.expanduser()
        logging.info(f"Consuming log file from {expanded_user_log_path}")
        f = subprocess.Popen(["tail", "-F", expanded_user_log_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while self._is_running:
            log_line = f.stdout.readline().decode(encoding="utf-8")
            self._notify_subscribers(log_line)
