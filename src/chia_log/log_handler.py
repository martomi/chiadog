# std
from typing import Optional

# project
from src.chia_log.handlers.daily_stats.stats_manager import StatsManager
from src.chia_log.handlers.harvester_activity_handler import HarvesterActivityHandler
from src.chia_log.handlers.finished_signage_point_handler import FinishedSignagePointHandler
from src.chia_log.log_consumer import LogConsumerSubscriber, LogConsumer
from src.notifier.notify_manager import NotifyManager


class LogHandler(LogConsumerSubscriber):
    """This class holds a list of handlers that analyze
    specific parts of the logs and generate events that
    are consumed by the notifier (for user notifications).

    Data flow:
        LogConsumer -> LogHandler -> Notifier

    Three easy steps to extend monitoring functionality
    1. Create a parser for a new part of the log stream
    2. Create a handler for analysing the parsed information
    3. Add the new handler to the list of handlers below
    """

    def __init__(
        self, log_consumer: LogConsumer, notify_manager: NotifyManager, stats_manager: Optional[StatsManager] = None
    ):
        self._notify_manager = notify_manager
        self._stats_manager = stats_manager
        self._handlers = [HarvesterActivityHandler(), FinishedSignagePointHandler()]
        log_consumer.subscribe(self)

    def consume_logs(self, logs: str):
        for handler in self._handlers:
            events = handler.handle(logs, self._stats_manager)
            self._notify_manager.process_events(events)
