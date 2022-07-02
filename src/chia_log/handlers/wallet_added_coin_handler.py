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

    def __init__(self, config: dict):
        self._parser = WalletAddedCoinParser()
        self._config_filters = None
        if config and config.get("enable"):
            logging.info("Enabled wallet_added_coin_handler")
            if config.get("filters"):
                logging.info("Detected filters in wallet_added_coin_handler")
                self._config_filters = config.get("filters")

    @staticmethod
    def __create_event(chia_coins: float) -> Event:
        xch_string = f"{chia_coins:.12f}".rstrip("0").rstrip(".")
        return Event(
            type=EventType.USER,
            priority=EventPriority.LOW,
            service=EventService.WALLET,
            message=f"Cha-ching! Just received {xch_string} XCH ☘️",
        )

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
            if self._config_filters and self._config_filters.get("transaction_amount"):
                transaction_amount_filter = float(self._config_filters.get("transaction_amount"))
                if chia_coins > transaction_amount_filter:
                    events.append(self.__create_event(chia_coins))
                else:
                    logging.info(
                        f"Filtering out chia received message since chia amount ${chia_coins} received is less than"
                        f"or equal to configured transaction_amount: ${transaction_amount_filter}")
            else:
                events.append(self.__create_event(chia_coins))

        return events
