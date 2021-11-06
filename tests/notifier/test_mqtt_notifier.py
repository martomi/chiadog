# std
import os
import unittest

# project
from src.notifier.mqtt_notifier import MqttNotifier
from .dummy_events import DummyEvents


class TestMqttNotifier(unittest.TestCase):
    def setUp(self) -> None:
        host = os.getenv("HOST")
        topic = os.getenv("TOPIC")
        username = os.getenv("MQTT_USERNAME")
        password = os.getenv("MQTT_PASSWORD")
        port = int(os.getenv("PORT", 1883))
        qos = int(os.getenv("QOS", 0))
        retain = bool(os.getenv("RETAIN", False))

        self.assertIsNotNone(host, "You must export HOST as env variable")
        self.assertIsNotNone(port, "You must export PORT as env variable")
        self.assertIsNotNone(topic, "You must export TOPIC as env variable")

        self.assertIn(
            qos, [0, 1, 2], "QoS level must be set to 0 (At most once), 1 (at least once) or " "2 (Exactly once)"
        )

        self.notifier = MqttNotifier(
            title_prefix="Test",
            config={
                "enable": True,
                "daily_stats": True,
                "wallet_events": True,
                "decreasing_plot_events": True,
                "increasing_plot_events": True,
                "topic": topic,
                "qos": qos,
                "retain": retain,
                "credentials": {
                    "host": host,
                    "port": port,
                    "username": username,
                    "password": password,
                },
            },
        )

    @unittest.skipUnless(os.getenv("TOPIC"), "Run only if MQTT topic available")
    def testMqttLowPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_low_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(os.getenv("TOPIC"), "Run only if MQTT topic available")
    def testMqttNormalPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_normal_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(os.getenv("TOPIC"), "Run only if MQTT topic available")
    def testMqttHighPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_high_priority_events())
        self.assertTrue(success)
