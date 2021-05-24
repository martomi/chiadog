# std
import unittest
from pathlib import Path

# project
from src.chia_log.handlers.daily_stats.stat_accumulators.signage_point_stats import SignagePointStats
from src.chia_log.parsers.finished_signage_point_parser import FinishedSignagePointParser


class TestSignagePointStats(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = FinishedSignagePointParser()
        self.stat_accumulator = SignagePointStats()
        self.example_logs_path = Path(__file__).resolve().parents[3] / "logs/finished_signage_point"

    def consumeLogFile(self, filename: str):
        with open(self.example_logs_path / filename, encoding="UTF-8") as f:
            logs = f.readlines()

        for log in logs:
            objects = self.parser.parse(log)
            for obj in objects:
                self.stat_accumulator.consume(obj)

    def testNominal(self):
        self.consumeLogFile("nominal.txt")
        self.assertEqual("Skipped SPs ✅️: None", self.stat_accumulator.get_summary())

    def testSkippedSignagePoints(self):
        self.consumeLogFile("skipped.txt")
        self.assertEqual("Skipped SPs ⚠️: 24 (32.00%)", self.stat_accumulator.get_summary())
        self.stat_accumulator.reset()
        self.assertEqual("Skipped SPs ⚠️: Unknown", self.stat_accumulator.get_summary())


if __name__ == "__main__":
    unittest.main()
