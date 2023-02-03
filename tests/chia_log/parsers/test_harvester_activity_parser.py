# std
import unittest
from pathlib import Path

# project
from src.chia_log.parsers import harvester_activity_parser


class TestHarvesterActivityParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = harvester_activity_parser.HarvesterActivityParser()
        self.example_logs_path = Path(__file__).resolve().parents[1] / "logs/harvester_activity"
        with open(self.example_logs_path / "nominal.txt", encoding="UTF-8") as f:
            self.nominal_logs = f.read()
        with open(self.example_logs_path / "nominal_old_log_format.txt", encoding="UTF-8") as f:
            self.nominal_logs_old_format = f.read()

    def tearDown(self) -> None:
        pass

    def testBasicParsing(self):
        for logs in [self.nominal_logs, self.nominal_logs_old_format]:
            # Check that important fields are correctly parsed
            activity_messages = self.parser.parse(logs)
            self.assertNotEqual(len(activity_messages), 0, "No log messages found")

            expected_eligible_plot_counts = [0, 1, 2, 3, 0]
            expected_proofs_found_counts = [0, 0, 1, 0, 0]
            expected_search_times = [0.55515, 1.05515, 0.23412, 0.12348, 0.34952]
            expected_total_plots_counts = [42, 42, 42, 43, 43]
            for msg, eligible, found, search, total in zip(
                activity_messages,
                expected_eligible_plot_counts,
                expected_proofs_found_counts,
                expected_search_times,
                expected_total_plots_counts,
            ):
                self.assertEqual(msg.eligible_plots_count, eligible, "Eligible plots count don't match")
                self.assertEqual(msg.found_proofs_count, found, "Found proofs count don't match")
                self.assertEqual(msg.search_time_seconds, search, "Search time seconds don't match")
                self.assertEqual(msg.total_plots_count, total, "Total plots count don't match")

            # Check arithmetic with parsed timestamps works
            prev_timestamp = activity_messages[0].timestamp
            for msg in activity_messages[1:]:
                seconds_since_last_activity = (msg.timestamp - prev_timestamp).seconds
                self.assertLess(seconds_since_last_activity, 10, "Unexpected duration between harvesting events")
                prev_timestamp = msg.timestamp


if __name__ == "__main__":
    unittest.main()
