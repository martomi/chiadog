# std
import os
import unittest

# project
from src.notifier import Event, EventType, EventPriority, EventService
from src.notifier.pushover_notifier import PushoverNotifier
from .dummy_events import DummyEvents


class TestPushoverNotifier(unittest.TestCase):
    def setUp(self) -> None:
        self.api_token = os.getenv("PUSHOVER_API_TOKEN")
        self.user_key = os.getenv("PUSHOVER_USER_KEY")
        self.assertIsNotNone(self.api_token, "You must export PUSHOVER_API_TOKEN as env variable")
        self.assertIsNotNone(self.user_key, "You must export PUSHOVER_USER_KEY as env variable")
        self.notifier = PushoverNotifier(
            title_prefix="Test",
            config={
                "enable": True,
                "daily_stats": True,
                "credentials": {"api_token": self.api_token, "user_key": self.user_key},
            },
        )

    @unittest.skipUnless(os.getenv("PUSHOVER_API_TOKEN"), "Run only if token available")
    def testLowPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_low_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(os.getenv("PUSHOVER_API_TOKEN"), "Run only if token available")
    def testNormalPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_normal_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(os.getenv("PUSHOVER_API_TOKEN"), "Run only if token available")
    def testHighPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_high_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(os.getenv("SHOWCASE_NOTIFICATIONS"), "Only for showcasing")
    def testShowcaseGoodNotifications(self):
        notifiers = [
            PushoverNotifier(
                title_prefix="Harvester 1",
                config={"enable": True, "api_token": self.api_token, "user_key": self.user_key},
            ),
            PushoverNotifier(
                title_prefix="Harvester 2",
                config={"enable": True, "api_token": self.api_token, "user_key": self.user_key},
            ),
            PushoverNotifier(
                title_prefix="Harvester 3",
                config={"enable": True, "api_token": self.api_token, "user_key": self.user_key},
            ),
        ]
        found_proof_event = Event(
            type=EventType.USER,
            priority=EventPriority.LOW,
            service=EventService.HARVESTER,
            message="Found 1 proof(s)!",
        )
        for notifier in notifiers:
            success = notifier.send_events_to_user(events=[found_proof_event])
            self.assertTrue(success)

    @unittest.skipUnless(os.getenv("SHOWCASE_NOTIFICATIONS"), "Only for showcasing")
    def testShowcaseBadNotifications(self):
        notifiers = [
            PushoverNotifier(
                title_prefix="Harvester 1",
                config={"enable": True, "api_token": self.api_token, "user_key": self.user_key},
            ),
            PushoverNotifier(
                title_prefix="Harvester 2",
                config={"enable": True, "api_token": self.api_token, "user_key": self.user_key},
            ),
            PushoverNotifier(
                title_prefix="Harvester 3",
                config={"enable": True, "api_token": self.api_token, "user_key": self.user_key},
            ),
        ]
        disconnected_hdd = Event(
            type=EventType.USER,
            priority=EventPriority.HIGH,
            service=EventService.HARVESTER,
            message="Disconnected HDD? The total plot count decreased from 101 to 42.",
        )
        network_issues = Event(
            type=EventType.USER,
            priority=EventPriority.NORMAL,
            service=EventService.HARVESTER,
            message="Experiencing networking issues? Harvester did not participate in any "
            "challenge for 120 seconds. It's now working again.",
        )
        offline = Event(
            type=EventType.USER,
            priority=EventPriority.HIGH,
            service=EventService.HARVESTER,
            message="Your harvester appears to be offline! No events for the past 712 seconds.",
        )
        events = [disconnected_hdd, offline, network_issues]
        for notifier, event in zip(notifiers, events):
            success = notifier.send_events_to_user(events=[event])
            self.assertTrue(success)
