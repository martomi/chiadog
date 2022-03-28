# std
import unittest
from pathlib import Path

# project
from src.chia_log.handlers.wallet_added_coin_handler import WalletAddedCoinHandler
from src.notifier import EventType, EventService, EventPriority


class TestWalledAddedCoinHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.handler = WalletAddedCoinHandler(config=None)
        self.example_logs_path = Path(__file__).resolve().parents[1] / "logs/wallet_added_coin"

    def testNominal(self):
        with open(self.example_logs_path / "nominal.txt", encoding="UTF-8") as f:
            logs = f.readlines()

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
        filter_handler = WalletAddedCoinHandler(config={
            'enable': "True",
            'filters': {
                'transaction_amount': "0.000000000001"
            }
        })
        with open(self.example_logs_path / "small_values.txt", encoding="UTF-8") as f:
            logs = f.readlines()
        events = filter_handler.handle("".join(logs))
        self.assertEqual(0, len(events))


if __name__ == "__main__":
    unittest.main()
