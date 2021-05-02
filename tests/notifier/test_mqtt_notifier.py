# std
import os
import unittest
from typing import Union, SupportsInt

# project
from src.notifier.mqtt_notifier import MqttNotifier
from .dummy_events import DummyEvents


class TestMqttNotifier(unittest.TestCase):
    def setUp(self) -> None:

        host = os.getenv("HOST")
        port = int(os.getenv("PORT"))
        topic = os.getenv("TOPIC")
        username = os.getenv("MQTT_USERNAME")
        password = os.getenv("MQTT_PASSWORD")
        qos = int(os.getenv("QOS"))

        self.assertIsNotNone(host, "You must export HOST as env variable")
        self.assertIsNotNone(port, "You must export PORT as env variable")
        self.assertIsNotNone(topic, "You must export TOPIC as env variable")

        if qos:
            self.assertIn(
                qos, [0, 1, 2], "QoS level must be set to 0 (At most once), 1 (at least once) or " "2 (Exactly once)"
            )

        self.notifier = MqttNotifier(
            title_prefix="Test",
            config={
                "enable": True,
                "daily_stats": True,
                "topic": topic,
                "qos": qos,
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
