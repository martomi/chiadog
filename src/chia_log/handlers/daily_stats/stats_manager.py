# std
import logging
from threading import Thread
from time import sleep
from typing import List

# project
from src.chia_log.handlers.daily_stats import StatReporter
from src.chia_log.handlers.daily_stats.stat_reporters.daily_stats_reporter import DailyStatsReporter
from src.chia_log.handlers.daily_stats.stat_reporters.http_reporter import HttpReporter
from src.chia_log.parsers.finished_signage_point_parser import FinishedSignagePointMessage
from src.chia_log.parsers.harvester_activity_parser import HarvesterActivityMessage
from src.config import Config
from src.notifier.notify_manager import NotifyManager


class StatsManager:
    """Initialize and manage all stat reporters and trigger their reporting.
    """

    def __init__(self, config: Config, notify_manager: NotifyManager):
        self._config = config.get_stats_config()
        self._notify_manager = notify_manager
        self._stats_reporter: dict[str, StatReporter] = {}
        self._initialize_stats_managers()

    def _initialize_stats_managers(self):
        key_notifier_mapping = {
            "http": HttpReporter,
            "daily_stats": DailyStatsReporter
        }

        for key in self._config.keys():
            if key not in key_notifier_mapping.keys():
                logging.warning(f"Cannot find mapping for {key} notifier.")
            if self._config[key]["enable"]:
                self._stats_reporter[key] = key_notifier_mapping[key](
                    notify_manager=self._notify_manager, config=self._config[key]
                )

        if len(self._stats_reporter.values()) == 0:
            logging.warning("No stats reporter enabled")
        else:
            # Start thread
            self._is_running = True
            self._thread = Thread(target=self._run_loop)
            self._thread.start()

    def consume_harvester_messages(self, objects: List[HarvesterActivityMessage]):
        for key in self._stats_reporter.keys():
            self._stats_reporter[key].consume_harvester_messages(objects)

    def consume_signage_point_messages(self, objects: List[FinishedSignagePointMessage]):
        for key in self._stats_reporter.keys():
            self._stats_reporter[key].consume_signage_point_messages(objects)

    def _run_loop(self):
        while self._is_running:
            for key in self._stats_reporter.keys():
                self._stats_reporter[key].report()
            sleep(1)

    def stop(self):
        self._is_running = False
