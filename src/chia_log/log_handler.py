# std
from typing import Optional, List, Type, Dict
import logging

# lib
from confuse import ConfigView

# project
from src.chia_log.handlers import LogHandlerInterface
from src.chia_log.handlers.daily_stats.stats_manager import StatsManager
from src.chia_log.handlers.harvester_activity_handler import HarvesterActivityHandler
from src.chia_log.handlers.partial_handler import PartialHandler
from src.chia_log.handlers.block_handler import BlockHandler
from src.chia_log.handlers.finished_signage_point_handler import FinishedSignagePointHandler
from src.chia_log.handlers.wallet_added_coin_handler import WalletAddedCoinHandler
from src.chia_log.handlers.wallet_peak_handler import WalletPeakHandler
from src.chia_log.handlers.wins_tracker import WinsTracker
from src.chia_log.log_consumer import LogConsumerSubscriber, LogConsumer
from src.notifier import EventService
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
        self,
        config: ConfigView,
        log_consumer: LogConsumer,
        notify_manager: NotifyManager,
        stats_manager: Optional[StatsManager] = None,
    ):
        self.services: Dict[EventService, List[Type[LogHandlerInterface]]] = {
            EventService.HARVESTER: [HarvesterActivityHandler],
            EventService.WALLET: [WalletAddedCoinHandler, WalletPeakHandler],
            EventService.FULL_NODE: [BlockHandler, FinishedSignagePointHandler],
            EventService.FARMER: [PartialHandler],
        }
        self._notify_manager = notify_manager
        self._stats_manager = stats_manager
        self._wins_tracker: Optional[WinsTracker] = None

        wins_config = config["wins_history"]
        if wins_config["enable"].get(bool):
            file_path = wins_config["file_path"].get(str)
            backup_dir = wins_config["backup_dir"].get()
            self._wins_tracker = WinsTracker(file_path=file_path, backup_dir=backup_dir)
            logging.info(f"Wins history tracking enabled: {file_path}")

        self._active_handlers = []
        for service, service_handlers in self.services.items():
            if service.name in config["monitored_services"].get(list):
                logging.info(f"Enabled service monitoring: {service.name}")
                for handler in service_handlers:
                    handler_instance = handler(config["handlers"][handler.config_name()])
                    if isinstance(handler_instance, HarvesterActivityHandler) and self._wins_tracker:
                        handler_instance.set_wins_tracker(self._wins_tracker)
                    self._active_handlers.append(handler_instance)
            else:
                logging.debug(f"Disabled service monitoring: {service.name}")
        log_consumer.subscribe(self)

    def consume_logs(self, logs: str):
        for handler in self._active_handlers:
            events = handler.handle(logs, self._stats_manager)
            self._notify_manager.process_events(events)
