# std
import logging
from typing import List, Optional

# project
from . import LogHandler
from ..parsers.wallet_added_coin_parser import WalletAddedCoinParser
from .daily_stats.stats_manager import StatsManager
from src.notifier import Event, EventService, EventType, EventPriority


class WalletAddedCoinHandler(LogHandler):
    """This handler parses all logs that report wallet
    receiving XCH and creates user notifications.
    """

    def __init__(self, prefix, symbol):
        self._parser = WalletAddedCoinParser(prefix)
        self.symbol = symbol

    def handle(self, logs: str, stats_manager: Optional[StatsManager] = None) -> List[Event]:
        events = []
        added_coin_messages = self._parser.parse(logs)
        if stats_manager:
            stats_manager.consume_wallet_messages(added_coin_messages)

        total_mojos = 0
        for coin_msg in added_coin_messages:
            logging.info(f"Cha-ching! Just received {coin_msg.amount_mojos} mojos.")
            total_mojos += coin_msg.amount_mojos

        if total_mojos > 0:
            chia_coins = total_mojos / 1e12
            xch_string = f"{chia_coins:.12f}".rstrip("0").rstrip(".")
            events.append(
                Event(
                    type=EventType.USER,
                    priority=EventPriority.LOW,
                    service=EventService.WALLET,
                    message=f"Cha-ching! Just received {xch_string} {self.symbol.upper()} ☘️",
                )
            )

        return events
