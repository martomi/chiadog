"""Log consumers are responsible for fetching chia logs
and propagating them to subscribers for further handling.

This abstraction should provide an easy ability to switch between
local file reader and fetching logs from a remote machine.
The latter has not been implemented yet. Feel free to add it.
"""

# std
import logging
from abc import ABC, abstractmethod
from pathlib import Path, PurePosixPath, PureWindowsPath, PurePath
from threading import Thread
from time import sleep
from typing import List, Optional, Tuple

# project
from src.config import Config
from src.config import check_keys
from src.util import OS

# lib
import paramiko
from paramiko.channel import ChannelStdinFile, ChannelStderrFile, ChannelFile
from pygtail import Pygtail  # type: ignore
from retry import retry


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
    def __init__(self, log_path: Path):
        super().__init__()
        logging.info("Enabled local file log consumer.")
        self._expanded_log_path = str(log_path.expanduser())
        self._offset_path = Config.get_log_offset_path()
        self._is_running = True
        self._thread = Thread(target=self._consume_loop)
        self._thread.start()
        self._log_size = 0

    def stop(self):
        logging.info("Stopping")
        self._is_running = False

    @retry((FileNotFoundError, PermissionError), delay=2)
    def _consume_loop(self):
        while self._is_running:
            sleep(1)  # throttle polling for new logs
            for log_line in Pygtail(self._expanded_log_path, read_from_end=True, offset_file=self._offset_path):
                self._notify_subscribers(log_line)


class NetworkLogConsumer(LogConsumer):
    """Consume logs over SSH from a remote harvester"""

    def __init__(
        self, remote_log_path: PurePath, remote_user: str, remote_host: str, remote_port: int, remote_platform: OS
    ):
        super().__init__()

        self._remote_user = remote_user
        self._remote_host = remote_host
        self._remote_port = remote_port
        self._remote_log_path = remote_log_path
        self._remote_platform = remote_platform
        self._log_size = 0

        self._ssh_client = paramiko.client.SSHClient()
        self._ssh_client.load_system_host_keys()
        self._ssh_client.connect(hostname=self._remote_host, username=self._remote_user, port=self._remote_port)

        # Start thread
        self._is_running = True
        self._thread = Thread(target=self._consume_loop)
        self._thread.start()

    def stop(self):
        logging.info("Stopping")
        self._is_running = False

    def _consume_loop(self):
        logging.info(
            f"Consuming remote log file {self._remote_log_path}"
            + f" from {self._remote_host}:{self._remote_port} ({self._remote_platform})"
        )


class PosixNetworkLogConsumer(NetworkLogConsumer):
    """Consume logs over SSH from a remote Linux/MacOS harvester"""

    def __init__(
        self, remote_log_path: PurePath, remote_user: str, remote_host: str, remote_port: int, remote_platform: OS
    ):
        logging.info("Enabled Posix network log consumer.")
        super(PosixNetworkLogConsumer, self).__init__(
            remote_log_path, remote_user, remote_host, remote_port, remote_platform
        )

    def _consume_loop(self):
        super(PosixNetworkLogConsumer, self)._consume_loop()

        stdin, stdout, stderr = self._ssh_client.exec_command(f"tail -F {self._remote_log_path}")

        while self._is_running:
            log_line = stdout.readline()
            self._notify_subscribers(log_line)


class WindowsNetworkLogConsumer(NetworkLogConsumer):
    """Consume logs over SSH from a remote Windows harvester"""

    def __init__(
        self, remote_log_path: PurePath, remote_user: str, remote_host: str, remote_port: int, remote_platform: OS
    ):
        logging.info("Enabled Windows network log consumer.")
        super(WindowsNetworkLogConsumer, self).__init__(
            remote_log_path, remote_user, remote_host, remote_port, remote_platform
        )

    def _consume_loop(self):
        super(WindowsNetworkLogConsumer, self)._consume_loop()

        stdin, stdout, stderr = self._read_log()

        while self._is_running:
            if self._has_rotated(self._remote_log_path):
                sleep(1)
                stdin, stdout, stderr = self._read_log()

            log_line = stdout.readline()
            self._notify_subscribers(log_line)

    def _read_log(self) -> Tuple[ChannelStdinFile, ChannelFile, ChannelStderrFile]:
        stdin, stdout, stderr = self._ssh_client.exec_command(
            f"powershell.exe Get-Content {self._remote_log_path} -Wait -Tail 1"
        )

        return stdin, stdout, stderr

    def _has_rotated(self, path: PurePath) -> bool:
        stdin, stdout, stderr = self._ssh_client.exec_command(f"powershell.exe Write-Host(Get-Item {str(path)}).length")

        old_size = self._log_size
        self._log_size = int(stdout.readline())

        return old_size > self._log_size


def get_host_info(host: str, user: str, path: str, port: int) -> Tuple[OS, PurePath]:

    client = paramiko.client.SSHClient()
    client.load_system_host_keys()
    client.connect(hostname=host, username=user, port=port)

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

    return OS.LINUX, PurePosixPath(path)


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

        # default SSH Port : 22
        remote_port = enabled_consumer_config.get("remote_port", 22)

        platform, path = get_host_info(
            enabled_consumer_config["remote_host"],
            enabled_consumer_config["remote_user"],
            enabled_consumer_config["remote_file_path"],
            remote_port,
        )

        if platform == OS.WINDOWS:
            return WindowsNetworkLogConsumer(
                remote_log_path=path,
                remote_host=enabled_consumer_config["remote_host"],
                remote_user=enabled_consumer_config["remote_user"],
                remote_port=remote_port,
                remote_platform=platform,
            )
        else:
            return PosixNetworkLogConsumer(
                remote_log_path=path,
                remote_host=enabled_consumer_config["remote_host"],
                remote_user=enabled_consumer_config["remote_user"],
                remote_port=remote_port,
                remote_platform=platform,
            )

    logging.error("Unhandled consumer type")
    return None
