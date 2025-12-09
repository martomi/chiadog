# std
import re
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

# lib
from dateutil import parser as dateutil_parser


@dataclass
class HarvesterActivityMessage:
    """Parsed information from harvester logs"""

    timestamp: datetime
    eligible_plots_count: int
    challenge_hash: str
    found_proofs_count: int
    search_time_seconds: float
    total_plots_count: int
    found_v1_proofs_count: Optional[int] = field(default=None)
    found_v2_qualities_count: Optional[int] = field(default=None)


class HarvesterActivityParser:
    """This class can parse info log messages from the chia harvester

    You need to have enabled "log_level: INFO" in your chia config.yaml
    The chia config.yaml is usually under ~/.chia/mainnet/config/config.yaml
    """

    def __init__(self):
        logging.debug("Enabled parser for harvester activity - eligible plot events.")
        self._regex_old = re.compile(
            r"([0-9:.]*) (?:[-0-9a-zA-Z.]+ )?harvester (?:src|chia).harvester.harvester(?:\s?): INFO\s*([0-9]+) plots were "
            r"eligible for farming ([0-9a-z.]*) Found ([0-9]) proofs. Time: ([0-9.]*) s. "
            r"Total ([0-9]*) plots"
        )
        self._regex_v2 = re.compile(
            r"([0-9T:.-]+) (?:[0-9.]+ )?harvester (?:src|chia).harvester.harvester(?:\s?): INFO\s+"
            r"challenge_hash: ([0-9a-f]+)\s+\.\.\.([0-9]+) plots were eligible for farming [a-z]*\s?"
            r"Found ([0-9]+) V1 proofs? and ([0-9]+) V2 qualit(?:y|ies)\. Time: ([0-9.]+) s\. "
            r"Total ([0-9]+) plots"
        )

    def parse(self, logs: str) -> List[HarvesterActivityMessage]:
        """Parses all harvester activity messages from a bunch of logs

        :param logs: String of logs - can be multi-line
        :returns: A list of parsed messages - can be empty
        """

        parsed_messages = []

        matches_old = self._regex_old.findall(logs)
        for match in matches_old:
            parsed_messages.append(
                HarvesterActivityMessage(
                    timestamp=dateutil_parser.parse(match[0]),
                    eligible_plots_count=int(match[1]),
                    challenge_hash=match[2],
                    found_proofs_count=int(match[3]),
                    search_time_seconds=float(match[4]),
                    total_plots_count=int(match[5]),
                )
            )

        matches_v2 = self._regex_v2.findall(logs)
        for match in matches_v2:
            v1_proofs = int(match[3])
            v2_qualities = int(match[4])
            parsed_messages.append(
                HarvesterActivityMessage(
                    timestamp=dateutil_parser.parse(match[0]),
                    eligible_plots_count=int(match[2]),
                    challenge_hash=match[1],
                    found_proofs_count=v1_proofs,
                    search_time_seconds=float(match[5]),
                    total_plots_count=int(match[6]),
                    found_v1_proofs_count=v1_proofs,
                    found_v2_qualities_count=v2_qualities,
                )
            )

        return parsed_messages
