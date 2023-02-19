# std
import logging
import os
import time
import unittest
from pathlib import Path

# lib
import confuse

# project
from src.chia_log.handlers.wallet_peak_handler import WalletPeakHandler
from src.notifier import EventType, EventService, EventPriority

logging.basicConfig(level=logging.DEBUG)

class TestWalledPeakHandler(unittest.TestCase):
    def setUp(self) -> None:
        config_dir = Path(__file__).resolve().parents[3]
        self.config = confuse.Configuration("chiadog", __name__)
        self.config.set_file(config_dir / "src/default_config.yaml")
        self.handler_config = self.config["handlers"][WalletPeakHandler.config_name()]

        self.handler = WalletPeakHandler(config=self.handler_config)
        self.example_logs_path = Path(__file__).resolve().parents[1] / "logs/wallet_peak"

        nominal_logs = ["nominal.txt", "nominal-tz-aware.txt"]
        partial_logs = ["partial-delay.txt"]
        self.nominal_logs = {}
        self.partial_logs = {}
        for name in nominal_logs:
            with open(self.example_logs_path / name, encoding="UTF-8") as f:
                self.nominal_logs[name] = f.readlines()
        for name in partial_logs:
            with open(self.example_logs_path / name, encoding="UTF-8") as f:
                self.partial_logs[name] = f.readlines()

        # Our TZ naive example logs are assumed to be in UTC
        os.environ["TZ"] = "UTC"
        time.tzset()

    def tearDown(self) -> None:
        self.config.clear()

    def testNominal(self):
        for name, log in self.nominal_logs.items():
            events = self.handler.handle("".join(log))
            self.assertEqual(10, len(events), f"Log: {name}")
            self.assertEqual(events[0].type, EventType.KEEPALIVE, "Unexpected event type")
            self.assertEqual(events[0].priority, EventPriority.NORMAL, "Unexpected priority")
            self.assertEqual(events[0].service, EventService.WALLET, "Unexpected service")
            self.assertEqual(events[0].message, "")

    def testPartialDelay(self):
        for name, log in self.partial_logs.items():
            events = self.handler.handle("".join(log))
            self.assertEqual(8, len(events), f"Log: {name}")
            self.assertEqual(events[0].type, EventType.KEEPALIVE, "Unexpected event type")
            self.assertEqual(events[0].priority, EventPriority.NORMAL, "Unexpected priority")
            self.assertEqual(events[0].service, EventService.WALLET, "Unexpected service")
            self.assertEqual(events[0].message, "")
