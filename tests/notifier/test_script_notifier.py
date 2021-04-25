# std
import unittest

# project
from src.notifier.script_notifier import ScriptNotifier
from .dummy_events import DummyEvents


class TestScriptNotifier(unittest.TestCase):
    def setUp(self) -> None:
        self.notifier = ScriptNotifier(
            title_prefix="Test",
            config={"enable": True, "daily_stats": True, "script_path": "tests/test_script.sh"},
        )

    def testLowPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_low_priority_events())
        self.assertTrue(success)

    def testNormalPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_normal_priority_events())
        self.assertTrue(success)

    def testHighPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_high_priority_events())
        self.assertTrue(success)
