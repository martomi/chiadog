# std
import logging
from typing import List

# project
from . import Event, Notifier
from .keep_alive_monitor import KeepAliveMonitor
from .pushover_notifier import PushoverNotifier
from .script_notifier import ScriptNotifier
from .smtp_notifier import SMTPNotifier
from .telegram_notifier import TelegramNotifier
from .discord_notifier import DiscordNotifier
from src.config import Config


class NotifyManager:
    """This class manages all notifiers and propagates
    events to all of them such that notifications can be
    delivered to multiple services at once.
    """

    def __init__(self, config: Config, keep_alive_monitor: KeepAliveMonitor = None):
        self._keep_alive_monitor = keep_alive_monitor or KeepAliveMonitor()
        self._keep_alive_monitor.set_notify_manager(self)
        self._notifiers: List[Notifier] = []
        self._config = config.get_notifier_config()
        self._notification_title_prefix = config.get_config()["notification_title_prefix"]
        self._initialize_notifiers()

    def _initialize_notifiers(self):
        key_notifier_mapping = {
            "pushover": PushoverNotifier,
            "script": ScriptNotifier,
            "telegram": TelegramNotifier,
            "discord": DiscordNotifier,
            "smtp": SMTPNotifier,
        }
        for key in self._config.keys():
            if key not in key_notifier_mapping.keys():
                logging.warning(f"Cannot find mapping for {key} notifier.")
            if self._config[key]["enable"]:
                self._notifiers.append(
                    key_notifier_mapping[key](title_prefix=self._notification_title_prefix, config=self._config[key])
                )
        if len(self._notifiers) == 0:
            logging.warning("Cannot process user events: 0 notifiers are enabled!")

    def process_events(self, events: List[Event]):
        """Process all keep-alive and user events"""
        if not len(events):
            return

        self._keep_alive_monitor.process_events(events)
        for notifier in self._notifiers:
            notifier.send_events_to_user(events)
