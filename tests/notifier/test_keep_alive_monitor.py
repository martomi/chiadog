# std
import logging
import unittest
from datetime import datetime
from time import sleep
from typing import List

# lib
import confuse

# project
from src.notifier import Event, EventService, EventType, EventPriority
from src.notifier.keep_alive_monitor import KeepAliveMonitor

logging.basicConfig(level=logging.DEBUG)


class DummyNotifyManager:
    def __init__(self, callback):
        self._callback = callback

    def process_events(self, events: List[Event]):
        if self._callback:
            self._callback(events)


class TestKeepAliveMonitor(unittest.TestCase):
    def setUp(self) -> None:
        self.threshold_seconds = 3
        self.config = confuse.Configuration("chiadog", __name__)
        self.config.set(
            {
                "enable_remote_ping": False,
                "ping_url": None,
                "notify_threshold_seconds": {
                    "HARVESTER": self.threshold_seconds,
                },
            }
        )
        self.keep_alive_monitor = KeepAliveMonitor(self.config)

        # Services that support keepalives
        self.services = [
            EventService.HARVESTER,
        ]
        # And their events
        self.keep_alive_events = [
            Event(type=EventType.KEEPALIVE, priority=EventPriority.NORMAL, service=EventService.HARVESTER, message=""),
        ]

    def tearDown(self) -> None:
        self.keep_alive_monitor.stop()
        self.config.clear()

    def testBasic(self):
        received_high_priority_event = False

        def callback(events: List[Event]):
            nonlocal received_high_priority_event
            self.assertEqual(len(events), len(self.services), "Unexpected number of events")
            self.assertEqual(events[0].type, EventType.USER, "Unexpected event type")
            self.assertEqual(events[0].priority, EventPriority.HIGH, "Unexpected event priority")
            received_high_priority_event = True

        notify_manager = DummyNotifyManager(callback)
        self.keep_alive_monitor.set_notify_manager(notify_manager)
        self.keep_alive_monitor.set_services(self.services)

        begin_tp = datetime.now()

        for _ in range(self.threshold_seconds):
            self.keep_alive_monitor.process_events(self.keep_alive_events)
            sleep(1)

        while not received_high_priority_event:
            logging.info(f"Waiting for high priority event, this should only take {self.threshold_seconds}s")
            sleep(1)

        end_tp = datetime.now()
        seconds_elapsed = (end_tp - begin_tp).seconds

        # Check that high priority event did not fire before keep-alive signal stopped
        self.assertGreater(seconds_elapsed, 2 * self.threshold_seconds - 1)


if __name__ == "__main__":
    unittest.main()
