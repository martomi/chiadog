# std
import re
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List

# lib
from dateutil import parser as dateutil_parser


@dataclass
class WalletAddedCoinMessage:
    timestamp: datetime
    amount_mojos: int


class WalletAddedCoinParser:
    """This class can parse info log messages from the chia wallet

    You need to have enabled "log_level: INFO" in your chia config.yaml
    The chia config.yaml is usually under ~/.chia/mainnet/config/config.yaml
    """

    def __init__(self, prefix):
        logging.info("Enabled parser for wallet activity - added coins.")
        self._prefix = prefix
        self._regex = re.compile(
            r"([0-9:.]*) wallet (?:src|" + prefix + ").wallet.wallet_state_manager(?:\s?): "
            r"INFO\s*Adding coin: {'amount': ([0-9]*),"
        )

    def parse(self, logs: str) -> List[WalletAddedCoinMessage]:
        """Parses all harvester activity messages from a bunch of logs

        :param logs: String of logs - can be multi-line
        :returns: A list of parsed messages - can be empty
        """

        parsed_messages = []
        matches = self._regex.findall(logs)
        for match in matches:
            # If Chives, we must multiply by 10,000 due to their fork choices
            mojos = int(match[1])
            if self._prefix == 'chives':
                mojos = mojos * 10000
            elif self._prefix == 'staicoin':
                mojos = mojos * 1000
            parsed_messages.append(
                WalletAddedCoinMessage(
                    timestamp=dateutil_parser.parse(match[0]),
                    amount_mojos=mojos,
                )
            )

        return parsed_messages
