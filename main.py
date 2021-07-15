# std
import argparse
import logging
import signal
import subprocess
import time
from argparse import Namespace, ArgumentParser
from pathlib import Path
from typing import Tuple

# project
from src.chia_log.handlers.daily_stats.stats_manager import StatsManager
from src.chia_log.log_consumer import create_log_consumer_from_config
from src.chia_log.log_handler import LogHandler
from src.config import Config, is_win_platform
from src.notifier.keep_alive_monitor import KeepAliveMonitor
from src.notifier.notify_manager import NotifyManager


def parse_arguments() -> Tuple[ArgumentParser, Namespace]:
    parser = argparse.ArgumentParser(
        description="ChiaFarmWatch: Watch your crops " "with a piece in mind for the yield."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--config', type=str, help="path to config.yaml")
    group.add_argument('--version', action='store_true')
    return parser, parser.parse_args()


def get_log_level(log_level: str) -> int:
    if log_level == "CRITICAL":
        return logging.CRITICAL
    if log_level == "ERROR":
        return logging.ERROR
    if log_level == "WARNING":
        return logging.WARNING
    if log_level == "INFO":
        return logging.INFO
    if log_level == "DEBUG":
        return logging.DEBUG

    logging.warning(f"Unsupported log level: {log_level}. Fallback to INFO level.")
    return logging.INFO


def init(config:Config):
    log_level = get_log_level(config.get_log_level_config())
    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
        level=log_level,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.info(f"Starting Chiadog ({version()})")

    # Remove the Pygtail offset file if it exists
    # Fixes a bug where hard reboot corrupts the offset file
    offset = Config.get_log_offset_path()
    if offset.exists():
        offset.unlink()

    # Create log consumer based on provided configuration
    chia_logs_config = config.get_chia_logs_config()
    log_consumer = create_log_consumer_from_config(chia_logs_config)
    if log_consumer is None:
        exit(0)

    # Keep a reference here so we can stop the thread
    # TODO: read keep-alive thresholds from config
    keep_alive_monitor = KeepAliveMonitor(config=config.get_keep_alive_monitor_config())

    # Notify manager is responsible for the lifecycle of all notifiers
    notify_manager = NotifyManager(config=config, keep_alive_monitor=keep_alive_monitor)

    # Stats manager accumulates stats over 24 hours and sends a summary each day
    stats_manager = StatsManager(config=config.get_daily_stats_config(), notify_manager=notify_manager)

    # Link stuff up in the log handler
    # Pipeline: Consume -> Handle -> Notify
    log_handler = LogHandler(log_consumer=log_consumer, notify_manager=notify_manager, stats_manager=stats_manager)

    def interrupt(signal_number, frame):
        if signal_number == signal.SIGINT:
            logging.info("Received interrupt. Stopping...")
            log_consumer.stop()
            keep_alive_monitor.stop()
            stats_manager.stop()
            exit(0)

    signal.signal(signal.SIGINT, interrupt)

    if is_win_platform():
        while True:
            try:
                time.sleep(5)
            except IOError:
                pass
    else:
        signal.pause()


def version():
    try:
        command_args = ["git", "describe", "--tags"]
        f = subprocess.Popen(command_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = f.communicate()
        return stdout.decode(encoding="utf-8").rstrip()
    except:
        return "unknown"


if __name__ == "__main__":
    # Parse config and configure logger
    argparse, args = parse_arguments()

    if args.config:
        conf = Config(Path(args.config))
        init(conf)
    elif args.version:
        print(version())
