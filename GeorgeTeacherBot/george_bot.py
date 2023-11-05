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
from lib.agents import BaseTableAgent
from lib.tools import create_agent_from_config
from lib.types import Triplet
from telegrambot import TelegramBot


KNOWN_LANGUAGE, TARGET_LANGUAGE = "russian", "english"
LANGUAGES: tp.Tuple[str, str] = (TARGET_LANGUAGE, KNOWN_LANGUAGE)
TIME_TO_WAIT: float = 0.1
HUMANLIKE_PROSSESING_TIME: float = 1.0
MAIN_STATE: str = "main_state"


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
        self._base: tp.Dict[str, Triplet] = dict()  # TODO: to think about rm
        self._triplet: Triplet = Triplet(),
        self._user_answer: str = ""
        self._return_context: tp.Optional[bool] = None
        self._error_message: str = ""
        self._messages_to_return: tp.Deque[str] = deque()
        self._keywords: tp.Dict[str, tp.Union[bool, int, float, str]] = dict()
        # TODO: make next line shorter
        self.load_words()
        agent_config["params"].update(  # TODO: make next line shorter
            {"state_to_legal_actions": {MAIN_STATE: set(self._base.values())}}
        )
        self._agent: BaseTableAgent = create_agent_from_config(
            **agent_config
        )  # TODO: use metaclass instead.
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
                for row in cursor:
                    for i in [0, 1]:
                        triplet = Triplet(
                            word_to_ask=row[LANGUAGES[i]],
                            language_to_ask=LANGUAGES[i],
                            word_to_answer=row[LANGUAGES[i ^ 1]],
                            language_to_answer=LANGUAGES[i ^ 1],
                            context=row["context"]  # TODO: get rid of duplication
                        )
                        # TODO: optimize memory usage
                        self._base.update({row[LANGUAGES[i]]: triplet})
        finally:
            connection.close()

    def update(self) -> tp.List[tp.Dict[str, str]]:
        self._agent.update(  # TODO: improve timestamp in extra_params.
            state=MAIN_STATE,
            action=self._triplet,
            reward=float(not self._is_answer_right),
            next_state=MAIN_STATE,
            extra_params={
                "timestamp": datetime.datetime.now().timestamp(),
                "is_it_a_pretrain_step": False
            }
        )
        self.load_words()
        self._agent.rewrite_states_and_actions(
            {MAIN_STATE: set(self._base.values())}
        )

    def _choose_triplet(self) -> None:
        triplet, waiting_time, debug_info = self._agent.get_action(MAIN_STATE)
        self._triplet = triplet
        self._waiting_time: float = waiting_time
        self._keywords.update(debug_info)
    
    def ask_word(self) -> None:
        self._choose_triplet()
        self.send_message(self._chat_id, self._triplet.word_to_ask)
   
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

    @staticmethod    
    def _check_words_similarity(
            s1: str, 
            s2: str,
            /,
            degree: int = 1
    ) -> bool:
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

        assert self._triplet.language_to_answer in LANGUAGES
        if self._triplet.language_to_answer == TARGET_LANGUAGE:
            sim_degree = 0
        elif self._triplet.language_to_answer == KNOWN_LANGUAGE:
            sim_degree = 1
        
        self._is_answer_right = self._check_words_similarity(
            self._triplet.word_to_answer,
            parts[0],
            degree=sim_degree
        )

        if self._is_answer_right:
            praise_message = np.random.choice(MESSAGES_WITH_PRAISE)
            self._messages_to_return.append(praise_message)
        else:
            condemnation_message = np.random.choice(MESSAGES_WITH_CONDEMNATION)
            self._messages_to_return.append(
                condemnation_message.format(self._triplet.word_to_answer)
            )

        if self._return_context:
            self._messages_to_return.extend(self._triplet.context.split("\\n"))

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
                        action=self._base[record["word_to_ask"]],
                        reward=float(not bool(record["is_answer_right"])),
                        next_state=MAIN_STATE,
                        extra_params={
                            "timestamp": int(record["timestamp"]),
                            "is_it_a_pretrain_step": True
                        }
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
                compacted_keywords = ";".join(
                    [
                        ",".join(
                            map(
                                lambda x: str(
                                    int(x) if isinstance(x, bool) else x
                                ),
                                key_and_value
                            )
                        ) for key_and_value in self._keywords.items()
                    ]
                )
                dicted_line = {
                    "timestamp": datetime.datetime.now().timestamp(),
                    "is_answer_right": self._is_answer_right,
                    "word_to_ask": repr(self._triplet.word_to_ask),
                    "word_to_answer": repr(self._triplet.word_to_answer),
                    "user_answer": repr(self._user_answer),
                    "error_message": repr(self._error_message),
                    "keywords": repr(compacted_keywords)
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
        self._keywords = dict()

