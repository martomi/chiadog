# std
import unittest
from pathlib import Path

# project
from src.chia_log.handlers import harvester_activity_handler
from src.notifier import EventType, EventService, EventPriority


class TestHarvesterActivityHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.handler = harvester_activity_handler.HarvesterActivityHandler()
        self.example_logs_path = Path(__file__).resolve().parents[1] / "logs/harvester_activity"

    def testNominal(self):
        with open(self.example_logs_path / "nominal.txt") as f:
            logs = f.readlines()

        for log in logs:
            events = self.handler.handle(log)
            self.assertEqual(len(events), 1, "Only expecting 1 event for keep-alive")
            self.assertEqual(events[0].type, EventType.KEEPALIVE, "Unexpected event type")
            self.assertEqual(events[0].priority, EventPriority.NORMAL, "Unexpected priority")
            self.assertEqual(events[0].service, EventService.HARVESTER, "Unexpected service")

    def testDecreasedPlots(self):
        with open(self.example_logs_path / "plots_decreased.txt") as f:
            logs = f.readlines()

        # Fourth log should trigger an event for a decreased plot count
        expected_number_events = [1, 1, 1, 2, 1]

        for log, number_events in zip(logs, expected_number_events):
            events = self.handler.handle(log)
            self.assertEqual(len(events), number_events, "Un-expected number of events")
            self.assertEqual(events[0].type, EventType.KEEPALIVE, "Unexpected event type")
            self.assertEqual(events[0].priority, EventPriority.NORMAL, "Unexpected priority")
            self.assertEqual(events[0].service, EventService.HARVESTER, "Unexpected service")
            if number_events == 2:
                self.assertEqual(events[1].type, EventType.USER, "Unexpected event type")
                self.assertEqual(events[1].priority, EventPriority.HIGH, "Unexpected priority")
                self.assertEqual(events[1].service, EventService.HARVESTER, "Unexpected service")
                self.assertEqual(events[1].message, "Disconnected HDD? The total plot count decreased from 43 to 30.")

    def testLostSyncTemporarily(self):
        with open(self.example_logs_path / "lost_sync_temporary.txt") as f:
            logs = f.readlines()

        # Fourth log should trigger an event for harvester outage
        expected_number_events = [1, 1, 1, 2, 1]

        for log, number_events in zip(logs, expected_number_events):
            events = self.handler.handle(log)
            self.assertEqual(len(events), number_events, "Un-expected number of events")
            self.assertEqual(events[0].type, EventType.KEEPALIVE, "Unexpected event type")
            self.assertEqual(events[0].priority, EventPriority.NORMAL, "Unexpected priority")
            self.assertEqual(events[0].service, EventService.HARVESTER, "Unexpected service")
            if number_events == 2:
                self.assertEqual(events[1].type, EventType.USER, "Unexpected event type")
                self.assertEqual(events[1].priority, EventPriority.NORMAL, "Unexpected priority")
                self.assertEqual(events[1].service, EventService.HARVESTER, "Unexpected service")
                self.assertEqual(
                    events[1].message,
                    "Experiencing networking issues? Harvester did not participate in any "
                    "challenge for 608 seconds. It's now working again.",
                )

    def testSlowSeekTime(self):
        with open(self.example_logs_path / "slow_seek_time.txt") as f:
            logs = f.readlines()

        for log in logs:
            events = self.handler.handle(log)
            self.assertEqual(len(events), 2, "Un-expected number of events")
            self.assertEqual(events[1].type, EventType.USER, "Unexpected event type")
            self.assertEqual(events[1].priority, EventPriority.NORMAL, "Unexpected priority")
            self.assertEqual(events[1].service, EventService.HARVESTER, "Unexpected service")
            self.assertEqual(events[1].message, "Seeking plots took too long: 28.12348 seconds!")


if __name__ == "__main__":
    unittest.main()
