# std
import unittest
from pathlib import Path

# project
from src.chia_log.parsers import finished_signage_point_parser


class TestFinishedSignagePointParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = finished_signage_point_parser.FinishedSignagePointParser()
        self.example_logs_path = Path(__file__).resolve().parents[1] / "logs/finished_signage_point"
        with open(self.example_logs_path / "nominal.txt", encoding="UTF-8") as f:
            self.nominal_logs = f.read()
        with open(self.example_logs_path / "nominal_old_log_format.txt", encoding="UTF-8") as f:
            self.nominal_logs_old_format = f.read()

    def tearDown(self) -> None:
        pass

    def testBasicParsing(self):
        for logs in [self.nominal_logs, self.nominal_logs_old_format]:
            # Check that important fields are correctly parsed
            signage_point_messages = self.parser.parse(logs)
            self.assertNotEqual(len(signage_point_messages), 0, "No log messages found")

            expected_sequence = list(range(62, 65)) + list(range(1, 65)) + list(range(1, 10))

            for signage_point_message, expected in zip(signage_point_messages, expected_sequence):
                self.assertEqual(signage_point_message.signage_point, expected)


if __name__ == "__main__":
    unittest.main()
