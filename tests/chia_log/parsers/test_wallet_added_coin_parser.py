# std
import unittest
from pathlib import Path

# project
from src.chia_log.parsers.wallet_added_coin_parser import WalletAddedCoinParser


class TestWalletAddedCoinParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = WalletAddedCoinParser()
        self.example_logs_path = Path(__file__).resolve().parents[1] / "logs/wallet_added_coin"
        with open(self.example_logs_path / "nominal.txt", encoding="UTF-8") as f:
            self.nominal_logs = f.read()

    def testBasicParsing(self):
        added_coins = self.parser.parse(self.nominal_logs)
        total_mojos = 0
        for coin in added_coins:
            total_mojos += coin.amount_mojos

        chia = total_mojos / 1e12
        self.assertEqual(2, chia)


if __name__ == "__main__":
    unittest.main()
