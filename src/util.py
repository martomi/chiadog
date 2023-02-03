import sys
from enum import Enum


class OS(Enum):
    LINUX = "LINUX"
    MACOS = "MACOS"
    WINDOWS = "WINDOWS"


def is_win_platform() -> bool:
    return sys.platform.startswith("win")
