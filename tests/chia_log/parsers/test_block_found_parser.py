# std
import unittest
from pathlib import Path

# project
from src.chia_log.parsers import block_parser


class TestBlockFoundParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = block_parser.BlockParser()
        self.example_logs_path = Path(__file__).resolve().parents[1] / "logs/block_found"
        with open(self.example_logs_path / "nominal.txt", encoding="UTF-8") as f:
            self.nominal_logs = f.read()

    def tearDown(self) -> None:
        pass

    def testBasicParsing(self):
        for logs in [self.nominal_logs]:
            activity_messages = self.parser.parse(logs)
            self.assertNotEqual(len(activity_messages), 0, "No log messages found")

            expected_eligible_block_counts = [1, 0]
            for msg, found in zip(
                activity_messages,
                expected_eligible_block_counts,
            ):
                self.assertEqual(msg.blocks_count, found, "Found block count don't match")


if __name__ == "__main__":
    unittest.main()
