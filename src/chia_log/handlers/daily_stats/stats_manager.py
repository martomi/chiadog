# std
import logging
from datetime import datetime, timedelta
from typing import List
from threading import Thread
from time import sleep

# project
from . import HarvesterActivityConsumer, FinishedSignageConsumer
from .stat_accumulators.eligible_plots_stats import EligiblePlotsStats
from .stat_accumulators.search_time_stats import SearchTimeStats
from .stat_accumulators.signage_point_stats import SignagePointStats
from .stat_accumulators.found_proof_stats import FoundProofStats
from .stat_accumulators.number_plots_stats import NumberPlotsStats
from src.chia_log.parsers.harvester_activity_parser import HarvesterActivityMessage
from src.chia_log.parsers.finished_signage_point_parser import FinishedSignagePointMessage
from src.notifier.notify_manager import NotifyManager
from src.notifier import Event, EventType, EventPriority, EventService


class StatsManager:
    """Manage all stat accumulators and trigger daily notification to the user
    with a summary from all stats that have been collected for the past 24 hours.
    """

    def __init__(self, config: dict, notify_manager: NotifyManager):
        try:
            self._enable = config["enable"]
            self._time_of_day = config["time_of_day"]
        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")
            self._enable = False

        if not self._enable:
            logging.warning("Disabled stats and daily notifications")
            return

        logging.info("Enabled stats for daily notifications")
        self._notify_manager = notify_manager
        self._stat_accumulators = [
            FoundProofStats(),
            SearchTimeStats(),
            NumberPlotsStats(),
            EligiblePlotsStats(),
            SignagePointStats(),
        ]

        logging.info(f"Summary notifications will be sent out daily at {self._time_of_day} o'clock")
        self._datetime_next_summary = datetime.now().replace(hour=self._time_of_day, minute=0, second=0, microsecond=0)
        if datetime.now() > self._datetime_next_summary:
            self._datetime_next_summary += timedelta(days=1)

        # Start thread
        self._is_running = True
        self._thread = Thread(target=self._run_loop)
        self._thread.start()

    def consume_harvester_messages(self, objects: List[HarvesterActivityMessage]):
        if not self._enable:
            return
        for stat_acc in self._stat_accumulators:
            if isinstance(stat_acc, HarvesterActivityConsumer):
                for obj in objects:
                    stat_acc.consume(obj)

    def consume_signage_point_messages(self, objects: List[FinishedSignagePointMessage]):
        if not self._enable:
            return
        for stat_acc in self._stat_accumulators:
            if isinstance(stat_acc, FinishedSignageConsumer):
                for obj in objects:
                    stat_acc.consume(obj)

    def _send_daily_notification(self):
        summary = "Hello farmer! 👋 Here's what happened in the last 24 hours:\n"
        for stat_acc in self._stat_accumulators:
            summary += "\n" + stat_acc.get_summary()
            stat_acc.reset()

        self._notify_manager.process_events(
            [Event(type=EventType.DAILY_STATS, priority=EventPriority.LOW, service=EventService.DAILY, message=summary)]
        )

    def _run_loop(self):
        while self._is_running:
            if datetime.now() > self._datetime_next_summary:
                self._send_daily_notification()
                self._datetime_next_summary += timedelta(days=1)
            sleep(1)

    def stop(self):
        self._is_running = False
