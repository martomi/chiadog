# std
import re
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List

# lib
from dateutil import parser as dateutil_parser


@dataclass
class FarmerServerMessage:
    """Parsed information from farmer_server logs"""

    timestamp: datetime
    peer_hash: str


class FarmerServerParser:
    """This class can parse info log messages from the chia farmer_server

    You need to have enabled "log_level: INFO" in your chia config.yaml
    The chia config.yaml is usually under ~/.chia/mainnet/config/config.yaml
    """

    def __init__(self):
        logging.info("Enabled parser for farmer_server activity - peer infos.")
        self._regex = re.compile(
            r"([0-9:.]*) farmer farmer_server\s*: INFO\s* <\- farming_info "
            r"from peer ([0-9a-z.]*) .*"
        )

    def parse(self, logs: str) -> List[FarmerServerMessage]:
        """Parses all farmer_server activity messages from a bunch of logs

        :param logs: String of logs - can be multi-line
        :returns: A list of parsed messages - can be empty
        """

        parsed_messages = []
        matches = self._regex.findall(logs)
        for match in matches:
            parsed_messages.append(
                FarmerServerMessage(
                    timestamp=dateutil_parser.parse(match[0]),
                    peer_hash=match[1],
                )
            )

        return parsed_messages
