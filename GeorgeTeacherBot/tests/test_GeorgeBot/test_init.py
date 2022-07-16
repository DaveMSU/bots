import sys; sys.path.append("/home/david_tyuman/telegram/bots/GeorgeTeacherBot")
import typing as tp

import dataclasses
import pytest
# import numpy as np

from global_vars import TOKEN, make_logger
from GeorgeBot import GeorgeBot

PATH_TO_WORDS_BASE = "./tests/test_GeorgeBot/test_words_base.txt"
CHAT_LOGGER = make_logger("ChatLogger", "./tests/test_GeorgeBot/test_logs/chat.log")
ML_LOGGER = make_logger("QLearningLogger", "./tests/test_GeorgeBot/test_logs/learning.log")
CHAT_ID = 746826672
NUMBER_OF_QUESTIONS = 2


@dataclasses.dataclass
class Case:
    alpha: float
    epsilon: float
    discount: float
    init_qvalue: float
    softmax_t: float
    name: tp.Optional[str] = None

    def __str__(self):
        if self.name:
            return self.name
        else:
            return f"bot: {self.alpha=}, {self.discount=}"


BOT_INITS = [
    Case(alpha=0.1, epsilon=1, discount=0.5, init_qvalue=4.0, softmax_t=0.01),
    Case(alpha=0.03, epsilon=0.1, discount=0.1, init_qvalue=10, softmax_t=0.4),
    Case(alpha=0.2, epsilon=0.9, discount=0.8, init_qvalue=4.0, softmax_t=1.0),
    Case(alpha=0.5, epsilon=0.2, discount=0.5, init_qvalue=2.0, softmax_t=0.5),
    Case(alpha=0.9, epsilon=0.5, discount=0.999, init_qvalue=4, softmax_t=2),
    Case(alpha=0.01, epsilon=1, discount=0.9, init_qvalue=3, softmax_t=0.1),
    Case(alpha=0.2, epsilon=0.3, discount=0.1, init_qvalue=0.0, softmax_t=3.5),
    Case(alpha=0.3, epsilon=0.2, discount=0.2, init_qvalue=0., softmax_t=0.1),
    Case(alpha=0.7, epsilon=1, discount=0.9, init_qvalue=0.1, softmax_t=0.01),
    Case(alpha=0.9, epsilon=0, discount=0.9999, init_qvalue=40, softmax_t=100)
]


@pytest.mark.parametrize("t", BOT_INITS, ids=str)
def test_bot_creation(t: Case) -> None:
    try:
        GeorgeBot(
            TOKEN,
            CHAT_ID,
            PATH_TO_WORDS_BASE,
            chat_logger=CHAT_LOGGER,
            ml_logger=ML_LOGGER,
            alpha=t.alpha,
            epsilon=t.epsilon,
            discount=t.discount,
            init_qvalue=t.init_qvalue,
            softmax_t=t.softmax_t
        )
    except BaseException as err:
        raise err
