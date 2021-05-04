# std
import http.client
import json
import logging
from datetime import datetime, timedelta
from typing import List

# project
from src.chia_log.handlers.daily_stats import StatReporter, HarvesterActivityConsumer, FinishedSignageConsumer
from src.chia_log.handlers.daily_stats.stat_accumulators.eligible_plots_stats import EligiblePlotsStats
from src.chia_log.handlers.daily_stats.stat_accumulators.found_proof_stats import FoundProofStats
from src.chia_log.handlers.daily_stats.stat_accumulators.number_plots_stats import NumberPlotsStats
from src.chia_log.handlers.daily_stats.stat_accumulators.search_time_stats import SearchTimeStats
from src.chia_log.handlers.daily_stats.stat_accumulators.signage_point_stats import SignagePointStats
from src.chia_log.parsers.finished_signage_point_parser import FinishedSignagePointMessage
from src.chia_log.parsers.harvester_activity_parser import HarvesterActivityMessage
from src.notifier.notify_manager import NotifyManager

REPORT_INTERVAL_MINUTES = 5


class HttpReporter(StatReporter):
    """Manage all stat accumulators and send regular status reports to a HTTP endpoint.
    """

    def __init__(self, config: dict, notify_manager: NotifyManager):
        self._datetime_next_report = datetime.now() + timedelta(minutes=REPORT_INTERVAL_MINUTES)

        try:
            self._enable = config["enable"]
            self._hostname = config["hostname"]
            self._path = config["path"]
        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")
            self._enable = False

        if not self._enable:
            logging.warning("Disabled HTTP reporter")
            return

        logging.info("Enabled HTTP reporter")

        self._stat_accumulators = [
            FoundProofStats(),
            SearchTimeStats(),
            NumberPlotsStats(),
            EligiblePlotsStats(),
            SignagePointStats(),
        ]

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

    def report(self):
        if datetime.now() > self._datetime_next_report:
            request_data = {
                "timestamp": int(datetime.now().timestamp()),
            }
            for stat_acc in self._stat_accumulators:
                request_data.update(stat_acc.get_data())
                stat_acc.reset()

            request_body = json.dumps(request_data)

            conn = http.client.HTTPSConnection(self._hostname)
            conn.request(
                "POST",
                self._path,
                request_body,
                {"Content-type": "application/json"},
            )
            response = conn.getresponse()
            if response.getcode() != 200:
                logging.warning(f"Problem reporting to HTTP endpoint, code: {response.getcode()}")
            else:
                logging.debug(f'Reported to HTTP endpoint.')

            conn.close()

            self._datetime_next_report += timedelta(minutes=REPORT_INTERVAL_MINUTES)
