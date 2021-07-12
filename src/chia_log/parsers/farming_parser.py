# std
import re
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List

# lib
from dateutil import parser as dateutil_parser


@dataclass
class FarmingMessage:
    """Parsed information from full node logs"""

    timestamp: datetime
    found_blocks_count: int
    submit_partials_count: int

class FarmingParser:
    """This class can parse info log messages from the chia farmer

    You need to have enabled "log_level: INFO" in your chia config.yaml
    The chia config.yaml is usually under ~/.chia/mainnet/config/config.yaml
    """

    def __init__(self):
        logging.info("Enabled parser for farming stats.")
        # Doing some "smart" tricks with this expression to also match the 64th signage point
        # with the same regex expression. See test examples to see how they differ.
        self._regex = re.compile(
            r"([0-9:.]*) farmer (?:src|chia).farmer.farmer\s*: INFO\s* (Submitting partial)"
            r"([0-9:.]*) full_node (?:src|chia).full_node.full_node\s*: INFO\s* (🍀\s* Farmed unfinished_block)"
        )

    def parse(self, logs: str) -> List[FarmingMessage]:
        """Parses all farmer activity messages from a bunch of logs

        :param logs: String of logs - can be multi-line
        :returns: A list of parsed messages - can be empty
        """

        parsed_messages = []
        matches = self._regex.findall(logs)
        for match in matches:
            parsed_messages.append(
                FarmingMessage(timestamp=dateutil_parser.parse(match[0]), submit_partials_count=1 if match[1] else 0, found_blocks_count=1 if match[2] else 0)
            )

        return parsed_messages
