# std
import unittest

# project
from src.notifier.script_notifier import ScriptNotifier
from .dummy_events import DummyEvents


class TestScriptNotifier(unittest.TestCase):
    def setUp(self) -> None:
        self.notifier = ScriptNotifier(
            title_prefix="Test", config={"enable": True, "script_path": "tests/test_script.sh"}
        )

    def testLowPriorityNotifications(self):
        errors = self.notifier.send_events_to_user(events=DummyEvents.get_low_priority_events())
        self.assertFalse(errors)

    def testNormalPriorityNotifications(self):
        errors = self.notifier.send_events_to_user(events=DummyEvents.get_normal_priority_events())
        self.assertFalse(errors)

    def testHighPriorityNotifications(self):
        errors = self.notifier.send_events_to_user(events=DummyEvents.get_high_priority_events())
        self.assertFalse(errors)
