import typing as tp


class LanguagePair(tp.NamedTuple):
    known: str
    target: str


def change_layout(line: str, type_of_keyboard: str = "eng-rus") -> str:
    assert type_of_keyboard == "eng-rus", "This keyboard is not handled yet."
    rus_eng_keyboard_layout = {
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
    return "".join(list(map(lambda c: KEYBOARD_LAYOUT.get(c, c), line)))


def levenstein_distance(s1: str, s2: str, /) -> int:
    distances_matrix = [
        list(range(len(s2) + 1)),
        [0] * (len(s2) + 1)
    ]
    prev_line_id, curr_line_id = 0, 1

    for i in range(len(s1) + 1):
        prev_line_id, curr_line_id = curr_line_id, prev_line_id
        if i == 0:
            continue
        else:
            for j in range(len(s2) + 1):
                if j == 0:
                    distances_matrix[curr_line_id][0] = \
                        distances_matrix[prev_line_id][0] + 1
                else:
                    distances_matrix[curr_line_id][j] = min(
                        distances_matrix[curr_line_id][j - 1] + 1,
                        distances_matrix[prev_line_id][j] + 1,
                        distances_matrix[prev_line_id][j - 1] + (
                            s1[i - 1] != s2[j - 1]
                        )
                    )
    return distances_matrix[curr_line_id][-1]
