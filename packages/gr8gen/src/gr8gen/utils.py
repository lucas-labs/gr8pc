from re import findall, sub
from typing import Literal

BLUE = '\033[94m'
GREEN = '\033[92m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RED = '\033[91m'
BRIGHT_BLUE = '\033[94;1m'
BRIGHT_GREEN = '\033[92;1m'
BRIGHT_MAGENTA = '\033[95;1m'
BRIGHT_CYAN = '\033[96;1m'
BRIGHT_RED = '\033[91;1m'
BOLD = '\033[1m'
DIM = '\033[2m'
UNDERLINE = '\033[4m'
RESET = '\033[0m'


def stl(
    text: str,
    *attrs: Literal[
        'blue',
        'green',
        'magenta',
        'cyan',
        'red',
        'bright_blue',
        'bright_green',
        'bright_magenta',
        'bright_cyan',
        'bright_red',
        'bold',
        'underline',
        'dim',
    ],
) -> str:
    # Collect all the ANSI codes for the specified attributes
    codes = [globals()[attr.upper()] for attr in attrs]
    return ''.join(codes) + text + RESET


def camel_to_snake(string: str) -> str:
    words: list[str] = findall(
        pattern=r'[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+', string=string
    )
    return '_'.join(map(lambda word: word.lower(), words))


def snake_to_camel(string: str) -> str:
    return sub(
        pattern=r'_([a-zA-Z])', repl=lambda match: match.group(1).upper(), string=string.title()
    )
