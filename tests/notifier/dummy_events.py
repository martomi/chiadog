# project
from src.notifier import Event, EventType, EventPriority, EventService


class DummyEvents:
    @staticmethod
    def get_low_priority_events():
        return [
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

    @staticmethod
    def get_normal_priority_events():
        return [
            Event(
                type=EventType.USER,
                priority=EventPriority.NORMAL,
                service=EventService.HARVESTER,
                message="Normal priority notification 1.",
            ),
        ]

    @staticmethod
    def get_high_priority_events():
        return [
            Event(
                type=EventType.USER,
                priority=EventPriority.HIGH,
                service=EventService.HARVESTER,
                message="High priority notification 1.",
            ),
        ]
