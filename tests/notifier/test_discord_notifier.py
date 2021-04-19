# std
import os
import unittest

# project
from src.notifier import Event, EventType, EventPriority, EventService
from src.notifier.discord_notifier import DiscordNotifier


class TestDiscordNotifier(unittest.TestCase):
    def setUp(self) -> None:
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.assertIsNotNone(webhook_url, "You must export DISCORD_WEBHOOK_URL as env variable")
        self.notifier = DiscordNotifier(
            title_prefix="Test", config={"enable": True, "webhook_url": webhook_url}
        )

    @unittest.skipUnless(os.getenv("DISCORD_WEBHOOK_URL"), "Run only if webhook available")
    def testDiscordLowPriorityNotifications(self):
        errors = self.notifier.send_events_to_user(
            events=[
                Event(
                    type=EventType.USER,
                    priority=EventPriority.LOW,
                    service=EventService.HARVESTER,
                    message="Low priority notification 1.",
                ),
                Event(
                    type=EventType.USER,
                    priority=EventPriority.LOW,
                    service=EventService.HARVESTER,
                    message="Low priority notification 2.",
                ),
            ]
        )
        self.assertFalse(errors)

    @unittest.skipUnless(os.getenv("DISCORD_WEBHOOK_URL"), "Run only if webhook available")
    def testDiscordNormalPriorityNotifications(self):
        errors = self.notifier.send_events_to_user(
            events=[
                Event(
                    type=EventType.USER,
                    priority=EventPriority.NORMAL,
                    service=EventService.HARVESTER,
                    message="Normal priority notification 1.",
                ),
                Event(
                    type=EventType.USER,
                    priority=EventPriority.NORMAL,
                    service=EventService.HARVESTER,
                    message="Normal priority notification 2.",
                ),
            ]
        )
        self.assertFalse(errors)

    @unittest.skipUnless(os.getenv("DISCORD_WEBHOOK_URL"), "Run only if webhook available")
    def testDiscordHighPriorityNotifications(self):
        errors = self.notifier.send_events_to_user(
            events=[
                Event(
                    type=EventType.USER,
                    priority=EventPriority.HIGH,
                    service=EventService.HARVESTER,
                    message="High priority notification 1.",
                ),
                Event(
                    type=EventType.USER,
                    priority=EventPriority.HIGH,
                    service=EventService.HARVESTER,
                    message="High priority notification 2.",
                ),
            ]
        )
        self.assertFalse(errors)
