import sys; sys.path.append("/home/david_tyuman/telegram_server/bots")  # TODO: remove that kinda import.

import datetime
import logging
import re
import time
import typing as tp
from collections import deque
from textwrap import dedent

import numpy as np
import pymysql

from global_vars import (
    MESSAGES_WITH_PRAISE, 
    MESSAGES_WITH_CONDEMNATION,
    change_layout
)
from lib.tools import create_agent_from_config
from telegrambot import TelegramBot


LANGUAGES = ["english", "russian"]
TIME_TO_WAIT = 0.1
HUMANLIKE_PROSSESING_TIME = 1.0
MAIN_STATE = "main_state"


class GeorgeBot(TelegramBot):
    def __init__(
            self,
            token: str, 
            db_password: str,
            chat_id: int,
            path_to_base: str,
            path_to_log: str,
            agent_config: tp.Dict[str, tp.Union[str, tp.Dict[str, float]]]
        ):
        TelegramBot.__init__(self, token)  # TODO: use super().
        self._db_password = db_password
        self._chat_id: int = chat_id
        self._path_to_base: str = path_to_base
        self._path_to_log: str = path_to_log
        self._base: tp.Dict[str, tp.Dict[str, str]] = dict()
        self._triplet: tp.Optional[tp.Dict[str, str]] = None
        self._user_answer: str = ""
        self._return_context: tp.Optional[bool] = None
        self._error_message: str = ""
        self._messages_to_return: tp.Deque[str] = deque()

        self.load_words()
        agent_config["params"].update(
            {"state_to_legal_actions": {MAIN_STATE: set(self._base)}}
        )
        self._agent = create_agent_from_config(**agent_config)  # TODO: use metaclass instead.
        self._waiting_time: tp.Optional[tp.Union[int, float]] = None

    def load_words(self) -> None:
        """
        Construct self._base atribute that have 
         next type: tp.Dict[str, tp.Dict[str, str]].
        """
        database_name, table_name = self._path_to_base.split(".")
        connection = pymysql.connect(  # TODO: remove hard code.
            host='localhost',
            user='root',
            password=self._db_password,
            db=database_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        try:
            with connection.cursor() as cursor:
                query = dedent(
                    f"""
                    SELECT * FROM {table_name};
                    """
                )
                cursor.execute(query)
                for raw in cursor:
                    for i in [0, 1]:
                        triplet = {
                            "ask": {
                                "word": raw[LANGUAGES[i]],
                                "language": LANGUAGES[i]
                            },
                            "answer": {
                                "word": raw[LANGUAGES[i ^ 1]],
                                "language": LANGUAGES[i ^ 1]
                            },
                            "context": raw["context"]  # TODO: remove double copy.
                        }
                        self._base.update({raw[LANGUAGES[i]]: triplet})
        finally:
            connection.close()        

    def update_base(self) -> tp.List[tp.Dict[str, str]]:
        self.load_words()
        self._agent.rewrite_states_and_actions(
            {MAIN_STATE: set(self._base)}
        )

    def _choose_triplet(self, base: tp.List[tp.Any]) -> tp.Dict[str, str]:
        word_to_ask, waiting_time = self._agent.get_action(MAIN_STATE)
        self._triplet = self._base[word_to_ask]
        self._waiting_time: float = waiting_time
    
    def ask_word(self) -> None:
        self._choose_triplet(self._base)
        self.send_message(self._chat_id, self._triplet["ask"]["word"])
   
    def wait_for_an_message(self) -> None:
        while True:
            time.sleep(TIME_TO_WAIT)
            message_data = self.look_for_new_message()
            if message_data:
                break
        assert isinstance(message_data, dict)
        self._user_answer = message_data["message"]["text"]

    @staticmethod
    def _lev_dist(s1: str, s2: str) -> int:
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
                        distances_matrix[curr_line_id][0] = distances_matrix[prev_line_id][0] + 1
                    else:
                        distances_matrix[curr_line_id][j] = min(
                            distances_matrix[curr_line_id][j - 1] + 1,
                            distances_matrix[prev_line_id][j] + 1,
                            distances_matrix[prev_line_id][j - 1] + (s1[i - 1] != s2[j - 1])
                        )
        return distances_matrix[curr_line_id][-1]

    @staticmethod    
    def _check_words_similarity(s1: str, s2: str, /, degree: int = 1) -> bool:
        lev_dist = min(
            GeorgeBot._lev_dist(s1.lower(), s2.lower()),
            GeorgeBot._lev_dist(change_layout(s1.lower()), s2.lower())
        )
        return lev_dist <= degree

    def process_the_message(self) -> None:
        self._error_message = ""
        parts = list(map(lambda x: x.strip(), self._user_answer.split('_')))
        if len(parts) > 2:
            self._error_message = (
                "Sorry, but you can enter a maximum of 2 words"
                f" separated by underscores! But you entered {len(parts)} words!"
            )
            self._messages_to_return.append(self._error_message)
            return None

        if len(parts) == 2 and parts[-1] != 'c':
            self._error_message = (
                "Sorry, but you entered an undefined identifier!\n"
                "At the moment I can only understand the id \'c\',"
                f" but \'{parts[-1]}\' has been received!"
            )
            self._messages_to_return.append(self._error_message)
            return None
            
        self._return_context = (parts[-1] == 'c')

        if self._triplet["answer"]["language"] == "english":
            sim_degree = 0
        elif self._triplet["answer"]["language"] == "russian":
            sim_degree = 1
        else:
            raise RuntimeError(
                f"No such language as triplet['answer']['language']=\"{self._triplet['answer']['language']}\"!"
            )
        
        self._is_answer_right = self._check_words_similarity(
            self._triplet["answer"]["word"],
            parts[0],
            degree=sim_degree
        )

        if self._is_answer_right:
            praise_message = np.random.choice(MESSAGES_WITH_PRAISE)
            self._messages_to_return.append(praise_message)
        else:
            condemnation_message = np.random.choice(MESSAGES_WITH_CONDEMNATION)
            self._messages_to_return.append(
                condemnation_message.format(self._triplet["answer"]["word"])
            )

        if self._return_context:
            self._messages_to_return.extend(self._triplet["context"].split("\\n"))

        self._agent.update(
            state=MAIN_STATE,
            action=self._triplet["ask"]["word"],
            reward=float(not self._is_answer_right),
            next_state=MAIN_STATE
        )

    def send_result(self) -> None:
        while len(self._messages_to_return):
            message = self._messages_to_return.popleft()
            self.send_message(self._chat_id, message)
            time.sleep(HUMANLIKE_PROSSESING_TIME)

    def pretrain(self) -> None: 
        database_name, table_name = self._path_to_log.split(".")
        connection = pymysql.connect(  # TODO: remove hard code.
            host='localhost',
            user='root',
            password=self._db_password,
            db=database_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with connection.cursor() as cursor:
                query = dedent(
                    f"""
                    SELECT * FROM {table_name};
                    """
                )
                cursor.execute(query)
                for record in cursor:
                    self._agent.update(
                        state=MAIN_STATE,
                        action=record["word_to_ask"],
                        reward=float(not bool(record["is_answer_right"])),
                        next_state=MAIN_STATE
                    )
        finally:
            connection.close()        

    def wait(self) -> None:
        time.sleep(self._waiting_time)

    def log_session(self) -> None:
        database_name, table_name = self._path_to_log.split(".")
        connection = pymysql.connect(  # TODO: remove hard code.
            host='localhost',
            user='root',
            password=self._db_password,
            db=database_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with connection.cursor() as cursor:
                dicted_line = {
                    "timestamp": datetime.datetime.now().timestamp(),
                    "is_answer_right": self._is_answer_right,
                    "word_to_ask": repr(self._triplet['ask']['word']),
                    "word_to_answer": repr(self._triplet['answer']['word']),
                    "user_answer": repr(self._user_answer),
                    "error_message": repr(self._error_message)
                }
                columns, values = zip(*dicted_line.items())
                query = dedent(
                    f"""
                    INSERT {table_name}(
                        {", ".join(columns)}
                    ) VALUES (
                        {", ".join(map(str, values))}
                    );       
                    """
                )
                cursor.execute(query)
            connection.commit()
        finally:
            connection.close()

