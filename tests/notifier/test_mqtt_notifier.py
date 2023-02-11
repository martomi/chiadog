# std
import os
import unittest

# lib
import confuse

# project
from src.notifier.mqtt_notifier import MqttNotifier
from .dummy_events import DummyEvents


class TestMqttNotifier(unittest.TestCase):
    def setUp(self) -> None:
        host = os.getenv("MQTT_HOST")
        topic = os.getenv("MQTT_TOPIC")
        username = os.getenv("MQTT_USERNAME")
        password = os.getenv("MQTT_PASSWORD")
        port = int(os.getenv("MQTT_PORT", 1883))
        qos = int(os.getenv("MQTT_QOS", 0))
        retain = bool(os.getenv("MQTT_RETAIN", False))

        self.assertIsNotNone(host, "You must export MQTT_HOST as env variable")
        self.assertIsNotNone(port, "You must export MQTT_PORT as env variable")
        self.assertIsNotNone(topic, "You must export MQTT_TOPIC as env variable")

        self.assertIn(
            qos, [0, 1, 2], "QoS level must be set to 0 (At most once), 1 (at least once) or " "2 (Exactly once)"
        )

        self.config = confuse.Configuration("chiadog", __name__)
        self.config.set(
            {
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
            }
        )

        self.notifier = MqttNotifier(
            title_prefix="Test",
            config=self.config,
        )

    @unittest.skipUnless(os.getenv("MQTT_TOPIC"), "Run only if MQTT topic available")
    def testMqttLowPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_low_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(os.getenv("MQTT_TOPIC"), "Run only if MQTT topic available")
    def testMqttNormalPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_normal_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(os.getenv("MQTT_TOPIC"), "Run only if MQTT topic available")
    def testMqttHighPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_high_priority_events())
        self.assertTrue(success)
