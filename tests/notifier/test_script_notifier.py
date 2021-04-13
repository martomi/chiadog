# std
import unittest

# project
from src.notifier import Event, EventType, EventPriority, EventService
from src.notifier.script_notifier import ScriptNotifier


class TestScriptNotifier(unittest.TestCase):
    def setUp(self) -> None:
        self.notifier = ScriptNotifier(
            title_prefix="Test", config={"enable": True, "script_path": "tests/test_script.sh"}
        )

    def testLowPriorityNotifications(self):
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

    def testNormalPriorityNotifications(self):
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

    def testHighPriorityNotifications(self):
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
