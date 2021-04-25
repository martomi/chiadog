# std
import os
import unittest

# project
from src.notifier.telegram_notifier import TelegramNotifier
from .dummy_events import DummyEvents


class TestTelegramNotifier(unittest.TestCase):
    def setUp(self) -> None:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.assertIsNotNone(bot_token, "You must export TELEGRAM_API_KEY as env variable")
        self.assertIsNotNone(chat_id, "You must export TELEGRAM_CHAT_ID as env variable")
        self.notifier = TelegramNotifier(
            title_prefix="Test",
            config={
                "enable": True,
                "daily_stats": True,
                "credentials": {"bot_token": bot_token, "chat_id": chat_id},
            },
        )

    @unittest.skipUnless(os.getenv("TELEGRAM_BOT_TOKEN"), "Run only if token available")
    def testTelegramLowPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_low_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(os.getenv("TELEGRAM_BOT_TOKEN"), "Run only if token available")
    def testTelegramNormalPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_normal_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(os.getenv("TELEGRAM_BOT_TOKEN"), "Run only if token available")
    def testTelegramHighPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_high_priority_events())
        self.assertTrue(success)
