from colorama import Fore, Back, Style, init
from enum import Enum
from functools import total_ordering


@total_ordering
class LogLevel(Enum):
    DEBUG = 1,
    INFO = 2,
    ERROR = 3

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented


class Log:

    @staticmethod
    def __info_stylized(message: str) -> str:
        return f'{Fore.LIGHTWHITE_EX}{message}{Style.RESET_ALL}'

    @staticmethod
    def __debug_stylized(message: str) -> str:
        return f'{Style.DIM + Fore.LIGHTGREEN_EX}{message}{Style.RESET_ALL}'

    @staticmethod
    def __error_stylized(message: str) -> str:
        return f'{Style.BRIGHT + Fore.RED} ERROR: {message}{Style.RESET_ALL}'

    def __init__(self, level: LogLevel):
        self.level: LogLevel = level
        init()

    def info(self, message: str):
        if self.level >= LogLevel.INFO:
            print(Log.__info_stylized(message))

    def debug(self, message: str):
        if self.level >= LogLevel.DEBUG:
            print(Log.__debug_stylized(message))

    def error(self, message: str):
        print(Log.__error_stylized(message))


__log = None


def get_logger(level: LogLevel = LogLevel.INFO):
    global __log

    if __log:
        return __log

    __log = Log(level)
    return __log
