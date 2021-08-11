# std
import unittest
from pathlib import Path

# project
from src.chia_log.handlers import block_handler
from src.notifier import EventType, EventService, EventPriority


class TestBlockFoundHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.handler = block_handler.BlockHandler()
        self.example_logs_path = Path(__file__).resolve().parents[1] / "logs/block_found"

    def testNominal(self):
        with open(self.example_logs_path / "nominal.txt", encoding="UTF-8") as f:
            logs = f.readlines()

        expected_number_events = [1, 0]
        for log, number_events in zip(logs, expected_number_events):
            events = self.handler.handle(log)
            self.assertEqual(len(events), number_events, "Un-expected number of events")
            if number_events == 1:
                self.assertEqual(events[0].type, EventType.USER, "Unexpected event type")
                self.assertEqual(events[0].priority, EventPriority.LOW, "Unexpected priority")
                self.assertEqual(events[0].service, EventService.FULL_NODE, "Unexpected service")


if __name__ == "__main__":
    unittest.main()
