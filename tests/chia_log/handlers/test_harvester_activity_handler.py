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
        with open(self.example_logs_path / "nominal.txt", encoding="UTF-8") as f:
            logs = f.readlines()

        for log in logs:
            events = self.handler.handle(log)
            keepAliveEvents = 0
            for event in events:
                if event.type == EventType.KEEPALIVE:
                    keepAliveEvents += 1
                    self.assertEqual(event.priority, EventPriority.NORMAL, "Unexpected priority")
                    self.assertEqual(event.service, EventService.HARVESTER, "Unexpected service")

            self.assertEqual(keepAliveEvents, 1, "Only expecting 1 event for keep-alive")

    def testDecreasedPlots(self):
        with open(self.example_logs_path / "plots_decreased.txt", encoding="UTF-8") as f:
            logs = f.readlines()
        plotDecreaseEventCount = 0
        for log in logs:
            events = self.handler.handle(log)
            for event in events:
                if event.type == EventType.PLOTDECREASE:
                    plotDecreaseEventCount += 1
                    self.assertEqual(event.priority, EventPriority.HIGH, "Unexpected priority")
                    self.assertEqual(event.service, EventService.HARVESTER, "Unexpected service")
                    self.assertEqual(event.message, "Disconnected HDD? The total plot count decreased from 43 to 30.")
        self.assertEqual(plotDecreaseEventCount, 1, "Only expecting 1 event for plotDecrease")

    def testIncreasedPlots(self):
        with open(self.example_logs_path / "plots_increased.txt", encoding="UTF-8") as f:
            logs = f.readlines()
        plotIncreaseEventCount = 0

        for log in logs:
            events = self.handler.handle(log)
            for event in events:
                if event.type == EventType.PLOTINCREASE:
                    plotIncreaseEventCount += 1
                    self.assertEqual(event.priority, EventPriority.LOW, "Unexpected priority")
                    self.assertEqual(event.service, EventService.HARVESTER, "Unexpected service")
                    if plotIncreaseEventCount == 1:
                        self.assertEqual(event.message, "Connected HDD? The total plot count increased from 0 to 40.")
                    elif plotIncreaseEventCount == 2:
                        self.assertEqual(event.message, "Connected HDD? The total plot count increased from 42 to 45.")

        self.assertEqual(plotIncreaseEventCount, 2, "Expecting 2 events for plotIncrease")

    def testLostSyncTemporarily(self):
        with open(self.example_logs_path / "lost_sync_temporary.txt", encoding="UTF-8") as f:
            logs = f.readlines()
        lostSyncEventCount = 0

        for log in logs:
            events = self.handler.handle(log)
            for event in events:
                if event.type == EventType.USER:
                    lostSyncEventCount += 1
                    self.assertEqual(event.type, EventType.USER, "Unexpected event type")
                    self.assertEqual(event.priority, EventPriority.NORMAL, "Unexpected priority")
                    self.assertEqual(event.service, EventService.HARVESTER, "Unexpected service")
                    self.assertEqual(
                        event.message,
                        "Experiencing networking issues? Harvester did not participate in any "
                        "challenge for 608 seconds. It's now working again.",
                    )
        self.assertEqual(lostSyncEventCount, 1, "Only expecting 1 event for lost sync event")

    def testSlowSeekTime(self):
        with open(self.example_logs_path / "slow_seek_time.txt", encoding="UTF-8") as f:
            logs = f.readlines()

        for log in logs:
            events = self.handler.handle(log)
            userEvents = 0

            for event in events:
                if event.type == EventType.USER:
                    userEvents += 1
                    self.assertEqual(event.type, EventType.USER, "Unexpected event type")
                    self.assertEqual(event.priority, EventPriority.NORMAL, "Unexpected priority")
                    self.assertEqual(event.service, EventService.HARVESTER, "Unexpected service")
                    self.assertEqual(event.message, "Seeking plots took too long: 28.12348 seconds!")

            self.assertEqual(userEvents, 1, "Only expecting 1 event for user")


if __name__ == "__main__":
    unittest.main()
