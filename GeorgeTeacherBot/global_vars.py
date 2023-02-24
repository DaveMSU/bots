import argparse
import json
import logging
import os
import sys
import typing as tp


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
    "And this... the right answer!",
    "You're right!",
    "You are sooo clever, right answer!",
    "Yeah! Fantastic!",
    "Ohh, you guessed it correctly!",
    "Ohh, you are... Inevitable!",
    "Best student ever! Yeah, it's right!",
    "Good!",
    "Yeah, right!",
    "Correct!",
    "You're awesome, dude!",
    "Yes, correct answer!",
    "Yes, correct!",
    "Right!",
    "You are correct!",
    "Yes! Right answer!"
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

