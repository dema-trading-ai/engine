import os

from typing import Literal
from rich.console import Console


def get_verbosity():
    return os.getenv("VERBOSITY") or "none"


def is_verbosity(verbosity: Literal["quiet", "debug", "none"]):
    return get_verbosity() == verbosity


console_standard = Console(color_system=None, width=200)
console_color = Console(color_system="truecolor", width=200)


class ConsoleColors:
    WARNING = '[bright_yellow]'
    ERROR = '[bright_red]'


def print_warning(text):
    if is_verbosity("quiet"):
        return
    console_standard.print("[WARNING] ", end='')
    console_color.print(f"{ConsoleColors.WARNING}{text}[/]")


def print_error(text):
    console_standard.print("[ERROR] ", end='')
    console_color.print(f"{ConsoleColors.ERROR}{text}[/]")


def print_config_error(text: str):
    console_standard.print("[CONFIG ERROR] ", end='')
    console_color.print(f"{ConsoleColors.ERROR}{text}[/]")


def print_info(text: str):
    if is_verbosity("quiet"):
        return
    console_standard.print(f"[INFO] {text}")


def print_debug(text: str):
    if is_verbosity("debug"):
        console_standard.print(f"[DEBUG] {text}")


def print_standard(text):
    console_standard.print(text)
