import argparse
import json
import logging
import os
import sys
import typing as tp


def parse_args() -> tp.Dict[str, bool]:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    return parser.parse_args()

def parse_config(config_path: str) -> tp.Dict[str, tp.Union[str, int]]:
    with open(config_path) as f:
        config = json.load(f)
    return config


def make_logger(
        logger_name: str,
        logging_file: tp.Union[str, bool],
        stdout: bool
    ) -> logging.Logger:
    """
    :param logger_name: just name of logger.
    :param logging_file: name of logging file,
    often ended with suffix '.log'. If false
    occured, then it is don't using FileHandler.
    :param stdout: Do add logging in stdout stream or don't.

    :return: a logger into which data could be written.
    """
    logger: logging.Logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    handlers: tp.List[logging.StreamHandler] = []
    if isinstance(logging_file, str):
        handlers.append(logging.FileHandler(logging_file))
    elif isinstance(logging_file, bool) and (logging_file == True):
        raise ValueError("'logging_file' variable shouldn't be True!")

    if stdout:
        handlers.append(logging.StreamHandler(sys.stdout))
    if not len(handlers):
        raise Exception(
            "There are no logging handlers, but"
            " there must be at least one handler."
        )

    for h in handlers:
        h.setLevel(logging.DEBUG)
        h.setFormatter(formatter)
        logger.addHandler(h)

    return logger


def change_layout(line: str) -> str:
    return "".join(list(map(lambda c: KEYBOARD_LAYOUT.get(c, c), line)))


TOKEN = os.environ["GEORGE_BOT_TOKEN"]

KEYBOARD_LAYOUT = {
    "q": "й", "w": "ц", "e": "у", "r": "к", "t": "е", "y": "н", 
    "u": "г", "i": "ш", "o": "щ", "p": "з", "[": "х", "]": "ъ",
    "a": "ф", "s": "ы", "d": "в", "f": "а", "g": "п", "h": "р", 
    "j": "о", "k": "л", "l": "д", ";": "ж", "'": "э", "\\": "ё",
    "z": "я", "x": "ч", "c": "с", "v": "м", "b": "и", "n": "т", 
    "m": "ь", ",": "б", ".": "ю",
    "й": "q", "ц": "w", "у": "e", "к": "r", "е": "t", "н": "y",
    "г": "u", "ш": "i", "щ": "o", "з": "p", "х": "[", "ъ": "]",
    "ф": "a", "ы": "s", "в": "d", "а": "f", "п": "g", "р": "h",
    "о": "j", "л": "k", "д": "l", "ж": ";", "э": "'", "ё": "\\",
    "я": "z", "ч": "x", "с": "c", "м": "v", "и": "b", "т": "n",
    "ь": "m", "б": ",", "ю": ".",
    "Q": "Й", "W": "Ц", "E": "У", "R": "К", "T": "Е", "Y": "Н", 
    "U": "Г", "I": "Ш", "O": "Щ", "P": "З", "{": "Х", "}": "Ъ",
    "A": "Ф", "S": "Ы", "D": "В", "F": "А", "G": "П", "H": "Р", 
    "J": "О", "K": "Л", "L": "Д", ":": "Ж", "\"": "Э", "|": "Ё",
    "Z": "Я", "X": "Ч", "C": "С", "V": "М", "B": "И", "N": "Т", 
    "M": "Ь", "<": "Б", ">": "Ю",
    'Й': 'Q', 'Ц': 'W', 'У': 'E', 'К': 'R', 'Е': 'T', 'Н': 'Y',
    'Г': 'U', 'Ш': 'I', 'Щ': 'O', 'З': 'P', 'Х': '{', 'Ъ': '}',
    'Ф': 'A', 'Ы': 'S', 'В': 'D', 'А': 'F', 'П': 'G', 'Р': 'H',
    'О': 'J', 'Л': 'K', 'Д': 'L', 'Ж': ':', 'Э': '"', 'Ё': '|',
    'Я': 'Z', 'Ч': 'X', 'С': 'C', 'М': 'V', 'И': 'B', 'Т': 'N',
    'Ь': 'M', 'Б': '<', 'Ю': '>'
}

MESSAGES_WITH_PRAISE = [
    "Good! It's right!",
    "Cool! This is the right answer!",
    "Great! You guessed it!\nOr maybe it's not accidental anymore?...)",
    "Cool, right!",
    "Another one right.",
    "Great!\nKeep going at this pace and soon you will have a vocabulary like mine.",
    "And this... the right answer!"
]

MESSAGES_WITH_CONDEMNATION = [
    "Uhhh.. you were wrong this time. The correct answer is \"{}\".",
    "Unfortunately, this is wrong. The correct answer was \"{}\".",
    "No, no luck this time. The answer is \"{}\".",
    "Answer is \"{}\"... but this is normal, because, as they say, \"practice makes perfect\"!",
    "No, sorry, answer is \"{}\". But keep going! Shit happens!",
    "No, unfortunately. I was expecting \"{}\".",
    "You are wrong, the answer is \"{}\"."
]

