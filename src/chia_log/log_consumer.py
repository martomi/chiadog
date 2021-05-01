"""Log consumers are responsible for fetching chia logs
and propagating them to subscribers for further handling.

This abstraction should provide an easy ability to switch between
local file reader and fetching logs from a remote machine.
The latter has not been implemented yet. Feel free to add it.
"""

# std
import logging
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path, PurePosixPath, PureWindowsPath, PurePath
from threading import Thread
from typing import List, Optional

# project
from src.config import check_keys, is_win_platform

# lib
import paramiko

from src.util import OS


class LogConsumerSubscriber(ABC):
    """Interface for log consumer subscribers (i.e. handlers)"""

    @abstractmethod
    def consume_logs(self, logs: str):
        """This method will be called when new logs are available"""
        pass


class LogConsumer(ABC):
    """Abstract class providing common interface for log consumers"""

    def __init__(self):
        self._subscribers: List[LogConsumerSubscriber] = []

    @abstractmethod
    def stop(self):
        pass

    def subscribe(self, subscriber: LogConsumerSubscriber):
        self._subscribers.append(subscriber)

    def _notify_subscribers(self, logs: str):
        for subscriber in self._subscribers:
            subscriber.consume_logs(logs)


class FileLogConsumer(LogConsumer):
    """Specific implementation for a simple file consumer"""

    def __init__(self, log_path: Path):
        logging.info("Enabled file log consumer.")
        super().__init__()
        self._log_path = log_path
        self._is_running = True
        self._thread = Thread(target=self._consume_loop)
        self._thread.start()

    def stop(self):
        logging.info("Stopping")
        self._is_running = False

    def _consume_loop(self):
        expanded_user_log_path = self._log_path.expanduser()
        logging.info(f"Consuming log file from {expanded_user_log_path}")

        if is_win_platform():
            consume_command_args = ["powershell.exe", "get-content", expanded_user_log_path, "-tail", "1", "-wait"]
        else:
            consume_command_args = ["tail", "-F", expanded_user_log_path]

        f = subprocess.Popen(consume_command_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while self._is_running:
            log_line = f.stdout.readline().decode(encoding="utf-8")
            self._notify_subscribers(log_line)


class NetworkLogConsumer(LogConsumer):
    """Consume logs over the network"""

    def __init__(self, remote_log_path: PurePath, remote_user, remote_host, remote_platform=OS.LINUX):
        logging.info("Enabled network log consumer.")
        super().__init__()

        self._remote_user = remote_user
        self._remote_host = remote_host
        self._remote_log_path = remote_log_path
        self._remote_platform = remote_platform

        self._ssh_client = paramiko.client.SSHClient()
        self._ssh_client.load_system_host_keys()
        self._ssh_client.connect(hostname=self._remote_host, username=self._remote_user)

        # Start thread
        self._is_running = True
        self._thread = Thread(target=self._consume_loop)
        self._thread.start()

    def stop(self):
        logging.info("Stopping")
        self._is_running = False

    def _consume_loop(self):
        logging.info(
            f"Consuming remote log file {self._remote_log_path} from {self._remote_host} ({self._remote_platform})"
        )

        if self._remote_platform == OS.WINDOWS:
            stdin, stdout, stderr = self._ssh_client.exec_command(
                f"powershell.exe Get-Content {self._remote_log_path} -Wait -Tail 1"
            )
        else:
            stdin, stdout, stderr = self._ssh_client.exec_command(f"tail -F {self._remote_log_path}")

        while self._is_running:
            log_line = stdout.readline()
            self._notify_subscribers(log_line)


def get_host_info(host: str, user: str, path: str):

    client = paramiko.client.SSHClient()
    client.load_system_host_keys()
    client.connect(hostname=host, username=user)

    stdin, stdout, stderr = client.exec_command("uname -a")
    fout: str = stdout.readline().lower()
    ferr: str = stderr.readline().lower()

    if "linux" in fout:
        return OS.LINUX, PurePosixPath(path)
    elif "darwin" in fout:
        return OS.MACOS, PurePosixPath(path)
    elif "not recognized" in ferr:
        return OS.WINDOWS, PureWindowsPath(path)
    else:
        logging.error("Found unsupported platform on remote host, assuming Linux and hope for the best.")

    return OS.LINUX


def create_log_consumer_from_config(config: dict) -> Optional[LogConsumer]:
    enabled_consumer = None
    for consumer in config.keys():
        if config[consumer]["enable"]:
            if enabled_consumer:
                logging.error("Detected multiple enabled consumers. This is unsupported configuration!")
                return None
            enabled_consumer = consumer
    if enabled_consumer is None:
        logging.error("Couldn't find enabled log consumer in config.yaml")
        return None

    enabled_consumer_config = config[enabled_consumer]

    if enabled_consumer == "file_log_consumer":
        if not check_keys(required_keys=["file_path"], config=enabled_consumer_config):
            return None
        return FileLogConsumer(log_path=Path(enabled_consumer_config["file_path"]))

    if enabled_consumer == "network_log_consumer":
        if not check_keys(
            required_keys=["remote_file_path", "remote_host", "remote_user"], config=enabled_consumer_config
        ):
            return None

        platform, path = get_host_info(
            enabled_consumer_config["remote_host"],
            enabled_consumer_config["remote_user"],
            enabled_consumer_config["remote_file_path"],
        )

        return NetworkLogConsumer(
            remote_log_path=path,
            remote_host=enabled_consumer_config["remote_host"],
            remote_user=enabled_consumer_config["remote_user"],
            remote_platform=platform,
        )

    logging.error("Unhandled consumer type")
    return None
