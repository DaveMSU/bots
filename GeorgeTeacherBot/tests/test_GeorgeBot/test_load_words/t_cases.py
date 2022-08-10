import dataclasses
import typing as tp

LANGUAGES = ["eng_word", "rus_word"]


@dataclasses.dataclass
class Case:
    content: str
    parsed_words_base: tp.Dict[str, tp.Dict[str, str]]
    name: tp.Optional[str] = None

    def __str__(self):
        if self.name:
            return self.name
        else:
            return f"{lines[:10]}"


TEST_CASES = [
    Case(
        content="maze - лабиринт  # There's a maze of lanes all round the village.",
        parsed_words_base={
            "maze": {
                "ask": {
                    "word": "maze",
                    "language": LANGUAGES[0]
                },
                "answer": {
                    "word": "лабиринт",
                    "language": LANGUAGES[1]
                },
                "comment": "There's a maze of lanes all round the village."
            },
            "лабиринт": {
                "ask": {
                    "word": "лабиринт",
                    "language": LANGUAGES[1]
                },
                "answer": {
                    "word": "maze",
                    "language": LANGUAGES[0]
                },
                "comment": "There's a maze of lanes all round the village."
            }
        },
        name="One line."
    ),
    Case(
        content="maze - лабиринт  # There's a maze of lanes all round the "
                "village.\nspan - промежуток  # A good life is not measured"
                " by any biblical span.",
        parsed_words_base={
            "maze": {
                "ask": {
                    "word": "maze",
                    "language": LANGUAGES[0]
                },
                "answer": {
                    "word": "лабиринт",
                    "language": LANGUAGES[1]
                },
                "comment": "There's a maze of lanes all round the village."
            },
            "лабиринт": {
                "ask": {
                    "word": "лабиринт",
                    "language": LANGUAGES[1]
                },
                "answer": {
                    "word": "maze",
                    "language": LANGUAGES[0]
                },
                "comment": "There's a maze of lanes all round the village."
            },
            "span": {
                "ask": {
                    "word": "span",
                    "language": LANGUAGES[0]
                },
                "answer": {
                    "word": "промежуток",
                    "language": LANGUAGES[1]
                },
                "comment": "A good life is not measured by any biblical span."
            },
            "промежуток": {
                "ask": {
                    "word": "промежуток",
                    "language": LANGUAGES[1]
                },
                "answer": {
                    "word": "span",
                    "language": LANGUAGES[0]
                },
                "comment": "A good life is not measured by any biblical span."
            }
        },
        name="Two lines."
    ),
    Case(
        content="have a checkup - пройти обследование  # There's a maze of"
                " lanes all round the village.\nspan - промежуток  # A good"
                " life is not measured by any biblical span.\napron - фартук"
                "  # No it's an environmental-friendly, recyclable apron.",
        parsed_words_base={
            "have a checkup": {
                "ask": {
                    "word": "have a checkup",
                    "language": LANGUAGES[0],
                },
                "answer": {
                    "word": "пройти обследование",
                    "language": LANGUAGES[1]
                },
                "comment": "There's a maze of lanes all round the village."
            },
            "пройти обследование": {
                "ask": {
                    "word": "пройти обследование",
                    "language": LANGUAGES[1],
                },
                "answer": {
                    "word": "have a checkup",
                    "language": LANGUAGES[0]
                },
                "comment": "There's a maze of lanes all round the village."
            },
            "span": {
                "ask": {
                    "word": "span",
                    "language": LANGUAGES[0]
                },
                "answer": {
                    "word": "промежуток",
                    "language": LANGUAGES[1]
                },
                "comment": "A good life is not measured by any biblical span."
            },
            "промежуток": {
                "ask": {
                    "word": "промежуток",
                    "language": LANGUAGES[1]
                },
                "answer": {
                    "word": "span",
                    "language": LANGUAGES[0]
                },
                "comment": "A good life is not measured by any biblical span."
            },
            "apron": {
                "ask": {
                    "word": "apron",
                    "language": LANGUAGES[0]
                },
                "answer": {
                    "word": "фартук",
                    "language": LANGUAGES[1]
                },
                "comment": "No it's an environmental-friendly, recyclable apron."
            },
            "фартук": {
                "ask": {
                    "word": "фартук",
                    "language": LANGUAGES[1]
                },
                "answer": {
                    "word": "apron",
                    "language": LANGUAGES[0]
                },
                "comment": "No it's an environmental-friendly, recyclable apron."
            }
        },
        name="Line with '-' in comment."
    ),
    Case(
        content="foo-boo - суп  # Фуу.. Бо-Бо когда-то упал..",
        parsed_words_base={
            "foo-boo": {
                "ask": {
                    "word": "foo-boo",
                    "language": LANGUAGES[0]
                },
                "answer": {
                    "word": "суп",
                    "language": LANGUAGES[1]
                },
                "comment": "Фуу.. Бо-Бо когда-то упал.."
            },
            "суп": {
                "ask": {
                    "word": "суп",
                    "language": LANGUAGES[1]
                },
                "answer": {
                    "word": "foo-boo",
                    "language": LANGUAGES[0]
                },
                "comment": "Фуу.. Бо-Бо когда-то упал.."
            }
        },
        name="A lot of '-' in all line."
    ),
    Case(
        content="slight - незначительный  # I look about for any "
                "confirmation, however slight, of my idea - and I find it.",
        parsed_words_base={
            "slight": {
                "ask": {
                    "word": "slight",
                    "language": LANGUAGES[0]
                },
                "answer": {
                    "word": "незначительный",
                    "language": LANGUAGES[1]
                },
                "comment": "I look about for any confirmation, "
                           "however slight, of my idea - and I find it."
            },
            "незначительный": {
                "ask": {
                    "word": "незначительный",
                    "language": LANGUAGES[1]
                },
                "answer": {
                    "word": "slight",
                    "language": LANGUAGES[0]
                },
                "comment": "I look about for any confirmation, "
                           "however slight, of my idea - and I find it."
            }
        },
        name="Line with ' - ' in comment."
    ),
    Case(
        content="inactive - неактивный  # - You're sure the Stargate's been inactive?",
        parsed_words_base={
            "inactive": {
                "ask": {
                    "word": "inactive",
                    "language": LANGUAGES[0]
                },
                "answer": {
                    "word": "неактивный",
                    "language": LANGUAGES[1]
                },
                "comment": "- You're sure the Stargate's been inactive?"
            },
            "неактивный": {
                "ask": {
                    "word": "неактивный",
                    "language": LANGUAGES[1]
                },
                "answer": {
                    "word": "inactive",
                    "language": LANGUAGES[0]
                },
                "comment": "- You're sure the Stargate's been inactive?"
            }
        },
        name="Direct speech in comment."
    )
]

