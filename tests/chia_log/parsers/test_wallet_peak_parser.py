# std
import unittest
import datetime
from pathlib import Path

# project
from src.chia_log.parsers.wallet_peak_parser import WalletPeakParser


class TestWalletPeakParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = WalletPeakParser()
        self.example_logs_path = Path(__file__).resolve().parents[1] / "logs/wallet_peak"
        with open(self.example_logs_path / "nominal.txt", encoding="UTF-8") as f:
            self.nominal_logs = f.read()

    def testBasicParsing(self):
        for nominal_logs in [self.nominal_logs]:
            peaks = self.parser.parse(nominal_logs)
            for peak in peaks:
                self.assertIsInstance(peak.peak, int)
                self.assertIsInstance(peak.peak_time, datetime.datetime)
                self.assertIsInstance(peak.log_time, datetime.datetime)
                self.assertNotEqual(peak.peak_time, peak.log_time)
