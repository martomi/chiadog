"""Notifier package responsible for user notification

"""

# std
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from enum import Enum
import logging


class EventPriority(Enum):
    """Event priority dictates how urgently
    the user needs to be notified about it
    """

    LOW = -1
    NORMAL = 0
    HIGH = 1


class EventType(Enum):
    """Events can either be user events
    that are propagated directly to the
    user, or keep-alive events that are
    processed to ensure the system runs
    """

    KEEPALIVE = 0
    USER = 1
    DAILY_STATS = 2


class EventService(Enum):
    """Even service helps to distinguish
    between similar events for different services
    """

    HARVESTER = 0
    FARMER = 1
    FULL_NODE = 2
    DAILY = 3


@dataclass
class Event:
    type: EventType
    priority: EventPriority
    service: EventService
    message: str


class Notifier(ABC):
    """This abstract class provides common interface for
    any notifier implementation. It should be easy to add
    extensions that integrate with variety of services such as
    Pushover, E-mail, Slack, WhatsApp, etc
    """

    def __init__(self, title_prefix: str, config: dict):
        self._title_prefix = title_prefix
        self._config = config
        self._conn_timeout_seconds = 10
        self._notification_types = [EventType.USER]
        self._notification_services = [EventService.HARVESTER, EventService.FARMER, EventService.FULL_NODE]

        try:
            if config["daily_stats"]:
                self._notification_types.append(EventType.DAILY_STATS)
                self._notification_services.append(EventService.DAILY)
        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")

    def get_title_for_event(self, event):
        icon = ""
        if event.priority == EventPriority.HIGH:
            icon = "🚨"
        elif event.priority == EventPriority.NORMAL:
            icon = "⚠️"
        elif event.priority == EventPriority.LOW:
            icon = "ℹ️"

        return f"{icon} {self._title_prefix} {event.service.name}"

    @abstractmethod
    def send_events_to_user(self, events: List[Event]) -> bool:
        """Implementation specific to the integration"""
        pass
