# std
import os
import unittest

# project
from src.notifier import Event, EventType, EventPriority, EventService
from src.notifier.pushover_notifier import PushoverNotifier


class TestPushoverNotifier(unittest.TestCase):
    def setUp(self) -> None:
        api_token = os.getenv("PUSHOVER_API_TOKEN")
        user_key = os.getenv("PUSHOVER_USER_KEY")
        self.assertIsNotNone(api_token, "You must export PUSHOVER_API_TOKEN as env variable")
        self.assertIsNotNone(user_key, "You must export PUSHOVER_USER_KEY as env variable")
        self.notifier = PushoverNotifier(
            title_prefix="Test", config={"enable": True, "api_token": api_token, "user_key": user_key}
        )

    def testLowPrioriyNotifications(self):
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

    def testNormalPrioriyNotifications(self):
        errors = self.notifier.send_events_to_user(
            events=[
                Event(
                    type=EventType.USER,
                    priority=EventPriority.NORMAL,
                    service=EventService.HARVESTER,
                    message="Normal priority notification.",
                )
            ]
        )
        self.assertFalse(errors)

    def testHighPrioriyNotifications(self):
        errors = self.notifier.send_events_to_user(
            events=[
                Event(
                    type=EventType.USER,
                    priority=EventPriority.HIGH,
                    service=EventService.HARVESTER,
                    message="This is a high priority notification!",
                )
            ]
        )
        self.assertFalse(errors)
