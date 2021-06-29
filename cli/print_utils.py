from rich.console import Console

console_standard = Console(color_system=None)
console_color = Console(color_system="truecolor")


class ConsoleColors:
    WARNING = '[bright_yellow]'
    ERROR = '[bright_red]'


def print_warning(text):
    console_standard.print("[WARNING] ", end='')
    console_color.print(f"{ConsoleColors.WARNING}{text}[/]")


def print_error(text):
    console_standard.print("[ERROR] ", end='')
    console_color.print(f"{ConsoleColors.ERROR}{text}[/]")


def print_config_error(text):
    console_standard.print("[CONFIG ERROR] ", end='')
    console_color.print(f"{ConsoleColors.ERROR}{text}[/]")


def print_info(text):
    console_standard.print(f"[INFO] {text}")


def print_standard(text):
    console_standard.print(text)
