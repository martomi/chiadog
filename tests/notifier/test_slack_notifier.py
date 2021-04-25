# std
import os
import unittest

# project
from src.notifier.slack_notifier import SlackNotifier
from .dummy_events import DummyEvents


class TestSlackNotifier(unittest.TestCase):
    def setUp(self) -> None:
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.assertIsNotNone(webhook_url, "You must export SLACK_WEBHOOK_URL as env variable")
        self.notifier = SlackNotifier(
            title_prefix="Test",
            config={
                "enable": True,
                "daily_stats": True,
                "credentials": {"webhook_url": webhook_url},
            },
        )

    @unittest.skipUnless(os.getenv("SLACK_WEBHOOK_URL"), "Run only if webhook available")
    def testSlackLowPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_low_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(os.getenv("SLACK_WEBHOOK_URL"), "Run only if webhook available")
    def testSlackNormalPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_normal_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(os.getenv("SLACK_WEBHOOK_URL"), "Run only if webhook available")
    def testSlackHighPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_high_priority_events())
        self.assertTrue(success)
