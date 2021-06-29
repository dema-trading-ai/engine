from rich import print as print_rich


class ConsoleColors:
    WARNING = '[bright_yellow]'
    ERROR = '[bright_red]'


def print_warning(text):
    print_rich(f"[WARNING] {ConsoleColors.WARNING}{text}[/]")


def print_error(text):
    print_rich(f"[ERROR] {ConsoleColors.ERROR}{text}[/]")


def print_config_error(text):
    print_rich(f"[CONFIG ERROR] {ConsoleColors.ERROR}{text}[/]")

def print_info(text):
    print_rich(f"[INFO] {text}")


def print_standard(text):
    print_rich(text)
