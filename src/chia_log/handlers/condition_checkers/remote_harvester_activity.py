# std
import logging
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

# project
from src.notifier import Event, EventService, EventType, EventPriority
from . import FarmerConditionChecker
from ...parsers.farmer_server_parser import FarmerServerMessage


@dataclass
class RemoteHarvester:
    """Record of last activity"""
    last_activity: datetime
    peer_hash: str
    ip_addr: str

class RemoteHarvesterActivity(FarmerConditionChecker):
    """The remote harvesters connected to the farmer_server
    are not expected to disappear. Disappearing remote harvesters
    indicate network or remote system issues.
    """

    def __init__(self):
        logging.info("Enabled check for disappearing remote harvesters.")
        self._warning_threshold = 300
        self._remote_harvesters = []

    def check(self, obj: FarmerServerMessage) -> Optional[Event]:
        #update last_activity
        is_new_harvester = True
        for i, remote_harvester in enumerate(self._remote_harvesters):
            if remote_harvester.peer_hash == obj.peer_hash:
                is_new_harvester = False
                self._remote_harvesters[i].last_activity = obj.timestamp
                break

        if is_new_harvester:
            new_harvester = RemoteHarvester(
                obj.timestamp,
                obj.peer_hash,
                obj.ip_addr
            )
            self._remote_harvesters.append(new_harvester)
            logging.info(f"New remote harvester: {obj.ip_addr}")


        event = None
        for i, remote_harvester in enumerate(self._remote_harvesters):
            seconds_since_last = (obj.timestamp - remote_harvester.last_activity).seconds
            if seconds_since_last > self._warning_threshold:
                message = (
                    f"Remote harvester offline: {remote_harvester.ip_addr} "
                    f"did not participate for {seconds_since_last} seconds!"
                )
                logging.warning(message)
                event = Event(
                    type=EventType.USER, priority=EventPriority.HIGH, service=EventService.FARMER, message=message
                )

                # Remove offline harvester
                self._remote_harvesters.pop(i)
                break

        return event
