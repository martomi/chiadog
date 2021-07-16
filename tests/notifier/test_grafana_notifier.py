# std
import os
import unittest

# project
from src.notifier.grafana_notifier import GrafanaNotifier
from .dummy_events import DummyEvents


class TestGrafanaNotifier(unittest.TestCase):
    def setUp(self) -> None:
        base_url = os.getenv("GRAFANA_BASE_URL")
        api_token = os.getenv("GRAFANA_API_TOKEN")
        self.assertIsNotNone(base_url, "You must export GRAFANA_BASE_URL as env variable")
        self.assertIsNotNone(api_token, "You must export GRAFANA_API_TOKEN as env variable")
        self.notifier = GrafanaNotifier(
            title_prefix="Test",
            config={
                "enable": True,
                "credentials": {
                    "base_url": base_url,
                    "api_token": api_token,
                },
            },
        )

    @unittest.skipUnless(
        os.getenv("GRAFANA_BASE_URL") and os.getenv("GRAFANA_API_TOKEN"), "Run only if credentials available"
    )
    def testGrafanaLowPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_low_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(
        os.getenv("GRAFANA_BASE_URL") and os.getenv("GRAFANA_BASE_URL"), "Run only if credentials available"
    )
    def testGrafanaNormalPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_normal_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(
        os.getenv("GRAFANA_BASE_URL") and os.getenv("GRAFANA_BASE_URL"), "Run only if credentials available"
    )
    def testGrafanaHighPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_high_priority_events())
        self.assertTrue(success)
