# std
import logging
from typing import List

# project
from . import LogHandler
from ..parsers.wallet_added_coin_parser import WalletAddedCoinParser
from src.notifier import Event, EventService, EventType, EventPriority


class WalletAddedCoinHandler(LogHandler):
    """This handler parses all logs that report wallet
    receiving XCH and creates user notifications.
    """

    def __init__(self):
        self._parser = WalletAddedCoinParser()

    def handle(self, logs: str) -> List[Event]:
        events = []
        added_coins = self._parser.parse(logs)

        total_mojos = 0
        for coin in added_coins:
            logging.info(f"Cha-ching! Just received {coin.amount_mojos} mojos.")
            total_mojos += coin.amount_mojos

        if total_mojos > 0:
            chia_coins = total_mojos / 1e12
            events.append(
                Event(
                    type=EventType.USER,
                    priority=EventPriority.LOW,
                    service=EventService.WALLET,
                    message=f"Cha-ching! Just received {chia_coins} XCH!",
                )
            )

        return events
