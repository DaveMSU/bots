import sys
sys.path.append("/home/david_tyuman/telegram/bot_instance.")
sys.path.append("/home/david_tyuman/telegram/bot_instance./GeorgeTeacherBot")

import os
import typing as tp

import pytest

from global_vars import TOKEN
from GeorgeBot import GeorgeBot
from tools import  make_logger
from t_cases import Case, TEST_CASES

# PATH_TO_WORDS_BASE = "../tests/test_words_base.txt"
PATH_TO_TMP_WORD_BASE = "./tests/test_tmp_words_base.txt"
LANGUAGES = ["eng_word", "rus_word"]
CHAT_ID = 746826672
CHAT_LOGGER = make_logger(
    "ChatLogger",
    "./tests/test_GeorgeBot/test_logs/chat.log",
    False
)
ML_LOGGER = make_logger(
    "QLearningLogger",
    "./tests/test_GeorgeBot/test_logs/learning.log",
    False
)


@pytest.fixture(scope="module")
def bot_instance():
    try:
        blank_file_path = "./test_blank_word_base.txt"
        with open(blank_file_path, "w") as f:
            f.write("\n")
        yield GeorgeBot(
            TOKEN,
            CHAT_ID,
            blank_file_path,
            chat_logger=CHAT_LOGGER,
            ml_logger=ML_LOGGER,
            alpha=0.1,
            epsilon=1.0,
            discount=0.5,
            init_qvalue=4.0,
            softmax_t=0.4
        )
    finally:
        if os.path.exists(blank_file_path):
            os.remove(blank_file_path) 
        

@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_dict_length_from_load_words_function(bot_instance: GeorgeBot, t: Case) -> None:
    try:
        with open(PATH_TO_TMP_WORD_BASE, "w") as f:
            f.write(t.content)
        bot_instance.load_words(PATH_TO_TMP_WORD_BASE)
        assert len(bot_instance._base) == len(t.parsed_words_base)
    finally:
        if os.path.exists(PATH_TO_TMP_WORD_BASE):
            os.remove(PATH_TO_TMP_WORD_BASE) 
        

@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_first_layer_dict_keys_from_load_words_function(bot_instance: GeorgeBot, t: Case) -> None:
    try:
        with open(PATH_TO_TMP_WORD_BASE, "w") as f:
            f.write(t.content)
        bot_instance.load_words(PATH_TO_TMP_WORD_BASE)
        for key, test_key in zip(
                sorted(bot_instance._base),
                sorted(t.parsed_words_base)
            ):
            assert key == test_key
    finally:
        if os.path.exists(PATH_TO_TMP_WORD_BASE):
            os.remove(PATH_TO_TMP_WORD_BASE) 

@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_first_layer_dict_values_type_from_load_words_function(bot_instance: GeorgeBot, t: Case) -> None:
    try:
        with open(PATH_TO_TMP_WORD_BASE, "w") as f:
            f.write(t.content)
        bot_instance.load_words(PATH_TO_TMP_WORD_BASE)
        for key, test_key in zip(
                sorted(bot_instance._base),
                sorted(t.parsed_words_base)
            ):
            assert type(bot_instance._base[key]) is type(t.parsed_words_base[test_key])
    finally:
        if os.path.exists(PATH_TO_TMP_WORD_BASE):
            os.remove(PATH_TO_TMP_WORD_BASE) 

@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_first_layer_dict_values_from_load_words_function(bot_instance: GeorgeBot, t: Case) -> None:
    try:
        with open(PATH_TO_TMP_WORD_BASE, "w") as f:
            f.write(t.content)
        bot_instance.load_words(PATH_TO_TMP_WORD_BASE)
        for key, test_key in zip(
                sorted(bot_instance._base),
                sorted(t.parsed_words_base)
            ):
            assert bot_instance._base[key] == t.parsed_words_base[test_key]
    finally:
        if os.path.exists(PATH_TO_TMP_WORD_BASE):
            os.remove(PATH_TO_TMP_WORD_BASE) 

@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_second_layer_keys_from_load_words_function(bot_instance: GeorgeBot, t: Case) -> None:
    try:
        with open(PATH_TO_TMP_WORD_BASE, "w") as f:
            f.write(t.content)
        bot_instance.load_words(PATH_TO_TMP_WORD_BASE)
        for key_1, test_key_1 in zip(
                sorted(bot_instance._base),
                sorted(t.parsed_words_base)
            ):
            for key_2, test_key_2 in zip(sorted(bot_instance._base[key_1]), sorted(t.parsed_words_base[test_key_1])):
                if isinstance(bot_instance._base[key_1], dict) and \
                    isinstance(t.parsed_words_base[key_1], dict):
                    assert key_2 == test_key_2
    finally:
        if os.path.exists(PATH_TO_TMP_WORD_BASE):
            os.remove(PATH_TO_TMP_WORD_BASE) 

@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_second_layer_values_types_from_load_words_function(bot_instance: GeorgeBot, t: Case) -> None:
    try:
        with open(PATH_TO_TMP_WORD_BASE, "w") as f:
            f.write(t.content)
        bot_instance.load_words(PATH_TO_TMP_WORD_BASE)
        for key_1, test_key_1 in zip(sorted(bot_instance._base), sorted(t.parsed_words_base)):
            for key_2, test_key_2 in zip(sorted(bot_instance._base[key_1]), sorted(t.parsed_words_base[test_key_1])):
                if isinstance(bot_instance._base[key_1], dict) and \
                    isinstance(t.parsed_words_base[key_1], dict):
                    assert type(bot_instance._base[key_1][key_2]) == \
                        type(t.parsed_words_base[test_key_1][test_key_2])
    finally:
        if os.path.exists(PATH_TO_TMP_WORD_BASE):
            os.remove(PATH_TO_TMP_WORD_BASE) 

@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_second_layer_values_from_load_words_function(bot_instance: GeorgeBot, t: Case) -> None:
    try:
        with open(PATH_TO_TMP_WORD_BASE, "w") as f:
            f.write(t.content)
        bot_instance.load_words(PATH_TO_TMP_WORD_BASE)
        for key_1, test_key_1 in zip(sorted(bot_instance._base), sorted(t.parsed_words_base)):
            for key_2, test_key_2 in zip(sorted(bot_instance._base[key_1]), sorted(t.parsed_words_base[test_key_1])):
                if isinstance(bot_instance._base[key_1], dict) and \
                    isinstance(t.parsed_words_base[key_1], dict):
                    assert bot_instance._base[key_1][key_2] == \
                        t.parsed_words_base[test_key_1][test_key_2]
    finally:
        if os.path.exists(PATH_TO_TMP_WORD_BASE):
            os.remove(PATH_TO_TMP_WORD_BASE) 

@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_direct_equivalence_of_test_dict_and_one_from_load_words_function(bot_instance: GeorgeBot, t: Case) -> None:
    try:
        with open(PATH_TO_TMP_WORD_BASE, "w") as f:
            f.write(t.content)
        bot_instance.load_words(PATH_TO_TMP_WORD_BASE)
        assert bot_instance._base == t.parsed_words_base
    finally:
        if os.path.exists(PATH_TO_TMP_WORD_BASE):
            os.remove(PATH_TO_TMP_WORD_BASE) 

@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_language_label_assignment_in_load_words_function(bot_instance: GeorgeBot, t: Case) -> None:
    try:
        with open(PATH_TO_TMP_WORD_BASE, "w") as f:
            f.write(t.content)
        bot_instance.load_words(PATH_TO_TMP_WORD_BASE)
        for key in bot_instance._base:
            observed_language = bot_instance._base[key]["ask"]["language"]
            test_language = t.parsed_words_base[key]["ask"]["language"]
            assert observed_language == test_language
    finally:
        if os.path.exists(PATH_TO_TMP_WORD_BASE):
            os.remove(PATH_TO_TMP_WORD_BASE)

