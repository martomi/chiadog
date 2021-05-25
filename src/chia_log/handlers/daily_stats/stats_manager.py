# std
import logging
from datetime import datetime, timedelta
from typing import List
from threading import Thread
from time import sleep

# project
from . import HarvesterActivityConsumer, WalletAddedCoinConsumer, FinishedSignageConsumer
from .stat_accumulators.eligible_plots_stats import EligiblePlotsStats
from .stat_accumulators.wallet_added_coin_stats import WalletAddedCoinStats
from .stat_accumulators.search_time_stats import SearchTimeStats
from .stat_accumulators.signage_point_stats import SignagePointStats
from .stat_accumulators.found_proof_stats import FoundProofStats
from .stat_accumulators.number_plots_stats import NumberPlotsStats
from src.chia_log.parsers.wallet_added_coin_parser import WalletAddedCoinMessage
from src.chia_log.parsers.harvester_activity_parser import HarvesterActivityMessage
from src.chia_log.parsers.finished_signage_point_parser import FinishedSignagePointMessage
from src.notifier.notify_manager import NotifyManager
from src.notifier import Event, EventType, EventPriority, EventService


class StatsManager:
    """Manage all stat accumulators and trigger daily notification to the user
    with a summary from all stats that have been collected for the past 24 hours.
    """

    def __init__(self, config: dict, notify_manager: NotifyManager, startup: bool = False):
        self._enable = config.get("enable", False)
        self._time_of_day = config.get("time_of_day", 21)
        self._frequency_hours = config.get("frequency_hours", 24)
        self._startup = startup

        if not self._enable:
            logging.warning("Disabled stats and daily notifications")
            return

        logging.info("Enabled stats for daily notifications")
        self._notify_manager = notify_manager
        self._stat_accumulators = [
            WalletAddedCoinStats(),
            FoundProofStats(),
            SearchTimeStats(),
            NumberPlotsStats(),
            EligiblePlotsStats(),
            SignagePointStats(),
        ]

        logging.info(
            f"Summary notifications will be sent out every {self._frequency_hours} "
            f"hours starting from {self._time_of_day} o'clock"
        )

        if self._startup:
            logging.info("An initial startup notification will be sent in 30 seconds")

        self._datetime_next_summary = datetime.now().replace(hour=self._time_of_day, minute=0, second=0, microsecond=0)
        while datetime.now() > self._datetime_next_summary:
            self._datetime_next_summary += timedelta(hours=self._frequency_hours)

        self._datetime_startup_summary = datetime.now().replace(microsecond=0)
        self._datetime_startup_summary += timedelta(seconds=30)

        # Start thread
        self._is_running = True
        self._thread = Thread(target=self._run_loop)
        self._thread.start()

    def consume_wallet_messages(self, objects: List[WalletAddedCoinMessage]):
        if not self._enable:
            return
        for stat_acc in self._stat_accumulators:
            if isinstance(stat_acc, WalletAddedCoinConsumer):
                for obj in objects:
                    stat_acc.consume(obj)

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

    def _send_daily_notification(self, startup: bool = False):
        if not startup:
            summary = f"Hello farmer! 👋 Here's what happened in the last {self._frequency_hours} hours:\n"
        else:
            summary = f"Hello farmer! 👋 This is a test summary to make sure your notifications are set up correctly:\n"

        for stat_acc in self._stat_accumulators:
            summary += "\n" + stat_acc.get_summary()
            if not startup:
                stat_acc.reset()

        self._notify_manager.process_events(
            [Event(type=EventType.DAILY_STATS, priority=EventPriority.LOW, service=EventService.DAILY, message=summary)]
        )

    def _run_loop(self):
        while self._is_running:
            if datetime.now() > self._datetime_next_summary:
                self._send_daily_notification()
                self._datetime_next_summary += timedelta(hours=self._frequency_hours)
            if self._startup and datetime.now() > self._datetime_startup_summary:
                self._send_daily_notification(startup=True)
                self._startup = False
            sleep(1)

    def stop(self):
        self._is_running = False
