# std
import datetime
import logging
from typing import List, Optional

# lib
from confuse import ConfigView

# project
from . import LogHandlerInterface
from ..parsers.wallet_peak_parser import WalletPeakParser
from .daily_stats.stats_manager import StatsManager
from src.notifier import Event, EventService, EventType, EventPriority


class WalletPeakHandler(LogHandlerInterface):
    """This handler parses all logs that report wallet
    receiving new peak updates and creates keepalive events based on their timeliness.
    """

    @staticmethod
    def config_name() -> str:
        return "wallet_peak_handler"

    def __init__(self, config: ConfigView):
        super().__init__(config)
        self._parser = WalletPeakParser()
        self.max_drift = config["max_drift_seconds"].get(int)
        logging.info(f"Allowing wallet processing drift of {self.max_drift}s.")

    def handle(self, logs: str, stats_manager: Optional[StatsManager] = None) -> List[Event]:
        events = []
        peak_messages = self._parser.parse(logs)

        for peak in peak_messages:
            drift = peak.log_time - peak.peak_time
            diff: str = self._context_aware_duration(drift)
            if drift.total_seconds() > 0.0 and drift.total_seconds() < self.max_drift:
                # Create a keep-alive event if the drift is small enough.
                # Diffs over the limit won't trigger keepalives,
                # which will eventually trigger a notification if not caught up.
                logging.debug(f"Wallet peak is up to speed, diff: {diff}")
                events.append(
                    Event(
                        type=EventType.KEEPALIVE, priority=EventPriority.NORMAL, service=EventService.WALLET, message=""
                    )
                )
            elif drift.total_seconds() < 0.0:
                logging.warning(f"Wallet peak is in the future, diff: {diff}")
            else:
                logging.warning(f"Wallet peak is falling behind, diff: {diff}")

        return events

    def _context_aware_duration(self, duration: datetime.timedelta) -> str:
        if duration.total_seconds() > 0.0 and duration < datetime.timedelta(minutes=30):
            return f"{duration.total_seconds():.0f}s"
        else:
            return f"{duration} (Are you sure your timezone is set correctly?)"
