# std
import unittest
from pathlib import Path

# project
from src.chia_log.handlers import farmer_server_handler
from src.notifier import EventType, EventService, EventPriority


class TestFarmerServerHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.handler = farmer_server_handler.FarmerServerHandler()
        self.example_logs_path = Path(__file__).resolve().parents[1] / "logs/farmer_server"

    def testNominal(self):
        with open(self.example_logs_path / "nominal.txt") as f:
            logs = f.readlines()

        for log in logs:
            events = self.handler.handle(log)
            self.assertEqual(len(events), 0, "Not expecting any events")

    def testDisconnectedHarvester(self):
        with open(self.example_logs_path / "disappearing_harvester.txt") as f:
            logs = f.readlines()

        expected_messages = [
            "Remote harvester offline: 255.255.255.255 did not participate for 385 seconds!",
        ]

        checked = 0
        for log in logs:
            events = self.handler.handle(log)
            if len(events) > 0:
                self.assertEqual(len(events), 1, "Expected a single event")
                self.assertEqual(events[0].type, EventType.USER, "Unexpected type")
                self.assertEqual(events[0].priority, EventPriority.HIGH, "Unexpected priority")
                self.assertEqual(events[0].service, EventService.FARMER, "Unexpected service")
                self.assertEqual(events[0].message, expected_messages[checked], "Unexpected message")
                checked += 1


if __name__ == "__main__":
    unittest.main()
