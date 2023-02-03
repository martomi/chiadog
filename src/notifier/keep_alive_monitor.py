# std
import logging
import urllib.request
from datetime import datetime
from threading import Thread
from time import sleep
from typing import List, Dict

# lib
from confuse import ConfigView

# project
from . import EventService, Event, EventType, EventPriority


class KeepAliveMonitor:
    """Runs a separate thread to monitor time passed
    since last keep-alive event was received (for all services)

    If a service stopped responding and is no longer
    sending events, this class will trigger a high priority
    user event and propagate it to the notifier.

    There's also an option to enable pinging to a remote service
    that provides a second layer of redundancy. E.g. if this monitoring
    thread crashes and stops responding, the remote service will stop
    receiving keep-alive ping events and can notify the user.
    """

    def __init__(self, config: ConfigView):
        self._notify_manager = None
        self.config = config

        # These will be set by set_services() once known
        self._last_keep_alive: Dict[EventService, datetime] = {}
        self._last_keep_alive_threshold_seconds: Dict[EventService, int] = {}

        self._ping_url = None
        if self.config["enable_remote_ping"].get(bool):
            self._ping_url = self.config["ping_url"].get()
            logging.info(f"Enabled remote pinging to {self._ping_url}")

        # Check period will be inferred from minimum threshold of all services.
        # Note that this period defines how often high priority notifications
        # will be re-triggered so < 5 min is not recommended
        self._check_period = float("inf")
        # No point in starting anything yet since we have no known services.
        self._is_running = False
        self._keep_alive_check_thread: Thread = Thread()

    def set_notify_manager(self, notify_manager):
        self._notify_manager = notify_manager

    def set_services(self, services: List[EventService]) -> None:
        # Reset values to fully overwrite services
        self._last_keep_alive = {}
        self._last_keep_alive_threshold_seconds = {}
        for service in services:
            # TODO: This check will become obsolete once all services emit keepalive events
            if service in [EventService.HARVESTER]:
                threshold = self.config["notify_threshold_seconds"][service.name].get(int)
                self._last_keep_alive[service] = datetime.now()
                self._last_keep_alive_threshold_seconds[service] = threshold
                logging.info(f"Keepalive monitor started for {service.name} with a threshold of {threshold}s")
            else:
                logging.debug(f"Keepalive not yet implemented for {service.name}, not enabling it.")

        # Calculate check period from lowest service value
        for threshold in self._last_keep_alive_threshold_seconds.values():
            self._check_period = min(threshold, self._check_period)

        logging.info(f"Keep-alive check period: {self._check_period} seconds")
        if self._check_period < 300:
            logging.warning(
                "Check period below 5 minutes might result "
                "in very frequent high priority notifications "
                "in case something stops working. Is it intended?"
            )
        # Start thread
        self._is_running = True
        self._keep_alive_check_thread = Thread(target=self.check_last_keep_alive)
        self._keep_alive_check_thread.start()

    def check_last_keep_alive(self):
        """This function runs in separate thread in the background
        and continuously checks that keep-alive events have been received
        """
        last_check = datetime.now()

        while self._is_running:
            sleep(1)  # Not sleeping entire check period so we can interrupt
            if (datetime.now() - last_check).seconds < self._check_period:
                continue
            last_check = datetime.now()
            self._ping_remote()

            events = []
            for service in self._last_keep_alive.keys():
                seconds_since_last = (datetime.now() - self._last_keep_alive[service]).seconds
                threshold = self._last_keep_alive_threshold_seconds[service]
                logging.debug(f"Keep-alive check for {service}: Last activity {seconds_since_last}s/{threshold}s")
                if seconds_since_last > threshold:
                    message = (
                        f"Your {service.name} appears to be offline! "
                        f"No events for the past {seconds_since_last} seconds."
                    )
                    logging.warning(message)
                    events.append(
                        Event(
                            type=EventType.USER,
                            priority=EventPriority.HIGH,
                            service=service,
                            message=message,
                        )
                    )
            if len(events):
                if self._notify_manager:
                    self._notify_manager.process_events(events)
                else:
                    logging.warning("Notify manager is not set - can't propagate high priority event!")

    def process_events(self, events: List[Event]):
        """Update last keep alive timestamp with any new keep-alive events"""

        for event in events:
            if event.type == EventType.KEEPALIVE:
                logging.debug(f"Received keep-alive event from {event.service.name}")
                self._last_keep_alive[event.service] = datetime.now()

    def _ping_remote(self):
        """Ping a remote watchdog that monitors that chiadog is alive
        and hasn't crashed silently. Second level of redundancy ;-)
        """

        if self._ping_url:
            logging.debug("Pinging remote keep-alive endpoint")
            try:
                urllib.request.urlopen(self._ping_url, timeout=10)
            except Exception as e:
                logging.error(f"Failed to ping keep-alive: {e}")

    def stop(self):
        logging.info("Stopping")
        self._is_running = False
