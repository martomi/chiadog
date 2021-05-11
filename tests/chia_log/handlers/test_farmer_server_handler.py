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
            self.assertEqual(len(events), 1, "Only expecting 1 event for keep-alive")
            self.assertEqual(events[0].type, EventType.KEEPALIVE, "Unexpected type")
            self.assertEqual(events[0].priority, EventPriority.NORMAL, "Unexpected priority")
            self.assertEqual(events[0].service, EventService.HARVESTER, "Unexpected service")

    def testDisconnectedHarvester(self):
        with open(self.example_logs_path / "disappearing_harvester.txt") as f:
            logs = f.readlines()

        expected_message = "Remote harvester offline: 255.255.255.255 did not participate for 385 seconds!"
        expected_number_events = [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1]

        checked = 0
        for log, number_events in zip(logs, expected_number_events):
            events = self.handler.handle(log)
            if len(events) > 0:
                print(len(events))
                self.assertEqual(len(events), number_events, "Unexpected number of events")
                self.assertEqual(events[0].type, EventType.KEEPALIVE, "Unexpected type")
                self.assertEqual(events[0].priority, EventPriority.NORMAL, "Unexpected priority")
                self.assertEqual(events[0].service, EventService.HARVESTER, "Unexpected service")
                if len(events) == 2:
                    self.assertEqual(events[1].type, EventType.USER, "Unexpected type")
                    self.assertEqual(events[1].priority, EventPriority.HIGH, "Unexpected priority")
                    self.assertEqual(events[1].service, EventService.FARMER, "Unexpected service")
                    self.assertEqual(events[1].message, expected_message, "Unexpected message")
                checked += 1


if __name__ == "__main__":
    unittest.main()
