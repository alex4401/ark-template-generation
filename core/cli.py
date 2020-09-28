import sys
from typing import Any
from pathlib import Path


def get_arg(name: str, default: Any) -> Any:
    name = '-' + name
    if name not in sys.argv:
        return default
    else:
        return sys.argv[sys.argv.index(name) + 1]


def get_bool(name: str) -> bool:
    name = '-' + name
    return name in sys.argv


def get_int(name: str, default: int) -> int:
    return int(get_arg(name, default))


def get_str(name: str, default: str) -> str:
    return get_arg(name, default)


def get_float(name: str, default: float) -> float:
    return float(get_arg(name, default))


def get_path(name: str, default: Path) -> Path:
    return Path(get_arg(name, default))