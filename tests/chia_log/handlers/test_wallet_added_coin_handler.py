# std
import unittest
from pathlib import Path
import copy

# lib
import confuse

# project
from src.chia_log.handlers.wallet_added_coin_handler import WalletAddedCoinHandler
from src.notifier import EventType, EventService, EventPriority


class TestWalledAddedCoinHandler(unittest.TestCase):
    def setUp(self) -> None:
        config_dir = Path(__file__).resolve().parents[3]
        self.config = confuse.Configuration("chiadog", __name__)
        self.config.set_file(config_dir / "src/default_config.yaml")
        self.handler_config = self.config["handlers"][WalletAddedCoinHandler.config_name()]

        self.handler = WalletAddedCoinHandler(config=self.handler_config)
        self.example_logs_path = Path(__file__).resolve().parents[1] / "logs/wallet_added_coin"

    def tearDown(self) -> None:
        self.config.clear()

    def testConfig(self):
        self.assertEqual(self.handler_config["min_mojos_amount"].get(int), 0)  # Dependent on default value being 0

    def testNominal(self):
        with open(self.example_logs_path / "nominal-before-1.4.0.txt", encoding="UTF-8") as f:
            logs_before = f.readlines()
        with open(self.example_logs_path / "nominal-after-1.4.0.txt", encoding="UTF-8") as f:
            logs_after = f.readlines()

        for logs in [logs_before, logs_after]:
            events = self.handler.handle("".join(logs))
            self.assertEqual(1, len(events))
            self.assertEqual(events[0].type, EventType.USER, "Unexpected event type")
            self.assertEqual(events[0].priority, EventPriority.LOW, "Unexpected priority")
            self.assertEqual(events[0].service, EventService.WALLET, "Unexpected service")
            self.assertEqual(events[0].message, "Cha-ching! Just received 2 XCH ☘️")

    def testFloatPrecision(self):
        with open(self.example_logs_path / "small_values.txt", encoding="UTF-8") as f:
            logs = f.readlines()

        events = self.handler.handle("".join(logs))
        self.assertEqual(1, len(events))
        self.assertEqual(events[0].type, EventType.USER, "Unexpected event type")
        self.assertEqual(events[0].priority, EventPriority.LOW, "Unexpected priority")
        self.assertEqual(events[0].service, EventService.WALLET, "Unexpected service")
        self.assertEqual(events[0].message, "Cha-ching! Just received 0.000000000001 XCH ☘️")

    def testTransactionAmountFilter(self):
        no_filter_config = self.handler_config
        filter_config = copy.deepcopy(self.handler_config)
        filter_config["min_mojos_amount"].set(5)

        filter_handler = WalletAddedCoinHandler(filter_config)
        no_filter_handler = WalletAddedCoinHandler(no_filter_config)
        with open(self.example_logs_path / "small_values.txt", encoding="UTF-8") as f:
            logs = f.readlines()
        filter_events = filter_handler.handle("".join(logs))
        self.assertEqual(0, len(filter_events))
        no_filter_events = no_filter_handler.handle("".join(logs))
        self.assertEqual(1, len(no_filter_events))


if __name__ == "__main__":
    unittest.main()
