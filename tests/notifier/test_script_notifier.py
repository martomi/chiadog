# std
import unittest

# lib
import confuse

# project
from src.notifier.script_notifier import ScriptNotifier
from .dummy_events import DummyEvents


class TestScriptNotifier(unittest.TestCase):
    def setUp(self) -> None:
        self.config = confuse.Configuration("chiadog", __name__)
        self.config.set(
            {
                "enable": True,
                "daily_stats": True,
                "wallet_events": True,
                "decreasing_plot_events": True,
                "increasing_plot_events": True,
                "script_path": "tests/test_script.sh",
            }
        )
        self.notifier = ScriptNotifier(
            title_prefix="Test",
            config=self.config,
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
