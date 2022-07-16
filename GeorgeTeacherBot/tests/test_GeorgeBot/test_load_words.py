import sys; sys.path.append("/home/david_tyuman/telegram/bots/GeorgeTeacherBot")
import os
import typing as tp

import dataclasses
import pytest

from global_vars import TOKEN, make_logger
from GeorgeBot import GeorgeBot

# PATH_TO_WORDS_BASE = "./tests/test_words_base.txt"
CHAT_LOGGER = make_logger("ChatLogger", "./tests/test_GeorgeBot/test_logs/chat.log")
ML_LOGGER = make_logger("QLearningLogger", "./tests/test_GeorgeBot/test_logs/learning.log")
CHAT_ID = 746826672
NUMBER_OF_QUESTIONS = 2


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

# lines="maze - лабиринт  # There's a maze of lanes all round the village.\\nspan - промежуток  # A good life is not measured by any biblical span.\\nsanity - вменяемость  # It protects her sanity.\\nevict - выселять  # They've turned up to evict him and he's not there.\\npivot - опорный  # Pivot table (SQL).\\nderive - выводить  # Using coiled springs, he derived the law of elasticity known today as Hooke's law.",


TEST_CASES = [
    Case(
        content="maze - лабиринт  # There's a maze of lanes all round the village.",
        parsed_words_base={
            "maze": {
                "word_to_ask": "maze",
                "word_to_answer": "лабиринт",
                "comment": "There's a maze of lanes all round the village."
            },
            "лабиринт": {
                "word_to_ask": "лабиринт",
                "word_to_answer": "maze",
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
                "word_to_ask": "maze",
                "word_to_answer": "лабиринт",
                "comment": "There's a maze of lanes all round the village."
            },
            "лабиринт": {
                "word_to_ask": "лабиринт",
                "word_to_answer": "maze",
                "comment": "There's a maze of lanes all round the village."
            },
            "span": {
                "word_to_ask": "span",
                "word_to_answer": "промежуток",
                "comment": "A good life is not measured by any biblical span."
            },
            "промежуток": {
                "word_to_ask": "промежуток",
                "word_to_answer": "span",
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
                "word_to_ask": "have a checkup",
                "word_to_answer": "пройти обследование",
                "comment": "There's a maze of lanes all round the village."
            },
            "пройти обследование": {
                "word_to_ask": "пройти обследование",
                "word_to_answer": "have a checkup",
                "comment": "There's a maze of lanes all round the village."
            },
            "span": {
                "word_to_ask": "span",
                "word_to_answer": "промежуток",
                "comment": "A good life is not measured by any biblical span."
            },
            "промежуток": {
                "word_to_ask": "промежуток",
                "word_to_answer": "span",
                "comment": "A good life is not measured by any biblical span."
            },
            "apron": {
                "word_to_ask": "apron",
                "word_to_answer": "фартук",
                "comment": "No it's an environmental-friendly, recyclable apron."
            },
            "фартук": {
                "word_to_ask": "фартук",
                "word_to_answer": "apron",
                "comment": "No it's an environmental-friendly, recyclable apron."
            }
        },
        name="Line with '-' in comment."
    ),
    Case(
        content="foo-boo - суп  # Фуу.. Бо-Бо когда-то упал..",
        parsed_words_base={
            "foo-boo": {
                "word_to_ask": "foo-boo",
                "word_to_answer": "суп",
                "comment": "Фуу.. Бо-Бо когда-то упал.."
            },
            "суп": {
                "word_to_ask": "суп",
                "word_to_answer": "foo-boo",
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
                "word_to_ask": "slight",
                "word_to_answer": "незначительный",
                "comment": "I look about for any confirmation, "
                           "however slight, of my idea - and I find it."
            },
            "незначительный": {
                "word_to_ask": "незначительный",
                "word_to_answer": "slight",
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
                "word_to_ask": "inactive",
                "word_to_answer": "неактивный",
                "comment": "- You're sure the Stargate's been inactive?"
            },
            "неактивный": {
                "word_to_ask": "неактивный",
                "word_to_answer": "inactive",
                "comment": "- You're sure the Stargate's been inactive?"
            }
        },
        name="Direct speech in comment."
    )
]


@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_load_word_lens(t: Case) -> None:
    tmp_path = "./test_tmp_word_base.txt"
    try:
        assert not os.path.exists(tmp_path),\
            f"File {tmp_path} exists, but it mustn't!"
        with open(tmp_path, "w") as f:
            f.write(t.content)
        bot = GeorgeBot(
            TOKEN,
            CHAT_ID,
            tmp_path,
            chat_logger=CHAT_LOGGER,
            ml_logger=ML_LOGGER,
            alpha=0.1,
            epsilon=1.0,
            discount=0.5,
            init_qvalue=4.0,
            softmax_t=0.4
        )
        bot.load_words(tmp_path)
        assert len(bot._base) == len(t.parsed_words_base)
        os.remove(tmp_path) 

    except BaseException as err:
        if os.path.exists(tmp_path):
            os.remove(tmp_path) 
        raise err

@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_load_words_keys(t: Case) -> None:
    tmp_path = "./test_tmp_word_base.txt"
    try:
        assert not os.path.exists(tmp_path),\
            f"File {tmp_path} exists, but it mustn't!"
        with open(tmp_path, "w") as f:
            f.write(t.content)
        bot = GeorgeBot(
            TOKEN,
            CHAT_ID,
            tmp_path,
            chat_logger=CHAT_LOGGER,
            ml_logger=ML_LOGGER,
            alpha=0.1,
            epsilon=1.0,
            discount=0.5,
            init_qvalue=4.0,
            softmax_t=0.4
        )
        bot.load_words(tmp_path)
        for key, test_key in zip(bot._base, t.parsed_words_base):
            assert key == test_key
        os.remove(tmp_path) 

    except BaseException as err:
        if os.path.exists(tmp_path):
            os.remove(tmp_path) 
        raise err

@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_load_words_data(t: Case) -> None:
    tmp_path = "./test_tmp_word_base.txt"
    try:
        assert not os.path.exists(tmp_path),\
            f"File {tmp_path} exists, but it mustn't!"
        with open(tmp_path, "w") as f:
            f.write(t.content)
        bot = GeorgeBot(
            TOKEN,
            CHAT_ID,
            tmp_path,
            chat_logger=CHAT_LOGGER,
            ml_logger=ML_LOGGER,
            alpha=0.1,
            epsilon=1.0,
            discount=0.5,
            init_qvalue=4.0,
            softmax_t=0.4
        )
        bot.load_words(tmp_path)
        for triplet, test_triplet in zip(
                bot._base.values(), 
                t.parsed_words_base.values()
            ):
            assert triplet["word_to_ask"] == test_triplet["word_to_ask"]
            assert triplet["word_to_answer"] == test_triplet["word_to_answer"]
            assert triplet["comment"] == test_triplet["comment"]
        os.remove(tmp_path) 

    except BaseException as err:
        if os.path.exists(tmp_path):
            os.remove(tmp_path) 
        raise err

