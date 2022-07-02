# std
import logging
from typing import List, Optional

# project
from . import LogHandlerInterface
from ..parsers.wallet_added_coin_parser import WalletAddedCoinParser
from .daily_stats.stats_manager import StatsManager
from src.notifier import Event, EventService, EventType, EventPriority


class WalletAddedCoinHandler(LogHandlerInterface):
    """This handler parses all logs that report wallet
    receiving XCH and creates user notifications.
    """

    @staticmethod
    def config_name() -> str:
        return "wallet_added_coin_handler"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self._parser = WalletAddedCoinParser()
        config = config or {}
        self.min_transaction_amount = config.get("min_transaction_amount", 0)
        logging.info(f"Wallet min_transaction_amount: {self.min_transaction_amount}")

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
            if chia_coins >= self.min_transaction_amount:
                events.append(self.__create_event(chia_coins))
            else:
                logging.debug(
                    f"Filtering out chia coin message since the amount ${chia_coins} received is less than"
                    f"the configured transaction_amount: ${self.min_transaction_amount}"
                )

        return events
