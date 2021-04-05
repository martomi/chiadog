# std
import unittest
from pathlib import Path

# project
from src.chia_log.handlers import finished_signage_point_handler
from src.notifier import EventType, EventService, EventPriority


class TestFinishedSignagePointHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.handler = finished_signage_point_handler.FinishedSignagePointHandler()
        self.example_logs_path = Path(__file__).resolve().parents[1] / "logs/finished_signage_point"

    def testNominal(self):
        with open(self.example_logs_path / "nominal.txt") as f:
            logs = f.readlines()

        # Currently not generating keep-alive events for the full node
        # based on the signage points because it's tightly coupled to
        # the eligible plots check from the harvester
        for log in logs:
            events = self.handler.handle(log)
            self.assertEqual(len(events), 0, "Not expecting any events")

    def testSkippedSignagePoints(self):
        with open(self.example_logs_path / "skipped.txt") as f:
            logs = f.readlines()

        expected_list = [(64, 16), (27, 29), (63, 1), (1, 9)]
        expected_messages = []
        for expected in expected_list:
            expected_messages.append(
                f"Experiencing networking issues? Skipped some signage points! "
                f"Last {expected[0]}/64, current {expected[1]}/64."
            )

        checked = 0
        for log in logs:
            events = self.handler.handle(log)
            if len(events) > 0:
                self.assertEqual(len(events), 1, "Expected a single event")
                self.assertEqual(events[0].type, EventType.USER, "Unexpected type")
                self.assertEqual(events[0].priority, EventPriority.NORMAL, "Unexpected priority")
                self.assertEqual(events[0].service, EventService.FULL_NODE, "Unexpected service")
                self.assertEqual(events[0].message, expected_messages[checked], "Unexpected message")
                checked += 1

    def testNetworkScramble(self):
        """This test case covers a case that I've observed happen on the actual mainnet
        where signage points are arriving completely out of order and in very rapid succession.
        It's currently unclear to me why this happens, but it seems to be network-wide issue
        rather than individual node problem. So this test checks that the handler is robust
        to ignoring these events and doesn't generate any false alarms for our node."""
        with open(self.example_logs_path / "scrambled.txt") as f:
            logs = f.readlines()

        for log in logs:
            events = self.handler.handle(log)
            self.assertEqual(len(events), 0)


if __name__ == "__main__":
    unittest.main()
