import sys
import traceback
from typing import Tuple

from cli import print_utils


class GeneralError(Exception):
    """Parent class inheriting from Exception"""


class ConfigError(GeneralError):
    pass


class WrongSpecTypeError(GeneralError):
    pass


class WrongSpecNameError(GeneralError):
    pass


class TimeframeNotSupportedByExchange(GeneralError):
    pass


class StoplossConfigError(GeneralError):
    pass


class PythonVersionError(GeneralError):
    pass


class ModeNotAvailableError(GeneralError):
    pass


class NotAStrategySubclassError(GeneralError):
    pass


class StrategyNotFoundError(GeneralError):
    pass


class StrategyConfigurationError(GeneralError):
    pass


class OfflineMissingDataError(GeneralError):
    pass


class ErrorOutput(GeneralError):
    """Error output module"""

    def __init__(self, exc_info: Tuple, add_info: str = '', stop: bool = False) -> None:
        self.type = exc_info[0].__name__
        self.tb = exc_info[-1]
        self.filename, self.line, self.func, self.text = traceback.extract_tb(self.tb)[-1]
        self.add_info = add_info
        self.stop = stop

    def __str__(self):
        default_text = f"A wild error appears!\n\t- Type: {self.type}\n\t- File: {self.filename}\n\t" \
                       f"- Function: {self.func}\n\t- Line: {self.line}"
        add_text = f"\n\t- Additional info: {self.add_info}"
        return default_text if len(self.add_info) == 0 else default_text + add_text

    def print_error(self):
        print_utils.print_error(self.__str__() + "\n\n\tExiting..." if self.stop else self.__str__())
        if self.stop:
            sys.exit(1)
