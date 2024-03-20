import sys; sys.path.append("/home/david_tyuman/telegram_server/bots")  # TODO: remove that kinda import.

import datetime
import time
import typing as tp
from collections import deque
from textwrap import dedent

import numpy as np
import pymysql

from global_vars import (
    MESSAGES_WITH_PRAISE,
    MESSAGES_WITH_CONDEMNATION,
)
from lib.agents import BaseTableAgent
from lib.teacher import ForeignLanguageTeacher
from lib.tools import create_agent_from_config
from lib.types import Triplet
from telegrambot import TelegramBot


TIME_TO_WAIT: float = 0.1
HUMANLIKE_PROSSESING_TIME: float = 1.0


class GeorgeBot(TelegramBot):
    def __init__(
            self,
            token: str,
            db_password: str,
            chat_id: int,
            teacher_config: to.Dict[str, tp.Union[str, dict]],
            path_to_the_log_file: str,
    ):
        TelegramBot.__init__(self, token)  # TODO: use super().
        self._db_password = db_password
        self._chat_id: int = chat_id
        self._teacher = ForeignLanguageTeacher(**teacher_config)
        self._log_path: str = path_to_the_log_file
        self._last_interaction: tp.Dict[str, tp.Any] = {
            "asked_triplet": None,
            "aswered_tripled": None,
            "was_the_answer_right": None,
            "error_message": None,
            "time_span_before_the_next_interaction": None,
            "waiting_time": None,
            "teachers_debug_info": None,
        }

    def update_itself(self) -> None:
        self._teacher.check_if_a_new_trained_agent_has_appeared_and_load_it()

    def ask(self) -> None:
        triplet = self._teacher.ask()
        self._last_interaction["asked_triplet"] = triplet

    def wait_for_a_message(self) -> str:
        while True:
            time.sleep(TIME_TO_WAIT)
            message_data = self.look_for_new_message()
            if message_data:
                break
        assert isinstance(message_data, dict)
        return message_data["message"]["text"]

    def process_the_message(self, message: str) -> tp.List[str]:
        error_message: str = ""
        messages_to_return: tp.List[str] = []

        # TODO: create specific class for the message
        parts = list(map(lambda x: x.strip(), message.split('_')))
        if len(parts) > 2:
            error_message = (
                "Sorry, but you can enter a maximum of 2 words separated by"
                f" underscores! But you entered {len(parts)} words!"
            )
            messages_to_return.append(self._error_message)
            return messages_to_return

        if len(parts) == 2 and parts[-1] != 'c':
            error_message = (
                "Sorry, but you entered an undefined identifier!\n"
                "At the moment I can only understand the id \'c\',"
                f" but \'{parts[-1]}\' has been received!"
            )
            messages_to_return.append(self._error_message)
            return messages_to_return

        should_the_context_be_returned: bool  = (parts[-1] == 'c')

        is_the_answer_right: bool
        context: str
        last_asked_triplet = self._last_interaction["asked_triplet"]
        right: bool = self.teacher.process_the_answer_and_the_question(
            received_answer=last_asked_tripletasked,
            received_answer=parts[0],
        )
        if right:
            praise_message = np.random.choice(MESSAGES_WITH_PRAISE)
            messages_to_return.append(praise_message)
        else:
            condemnation_message = np.random.choice(MESSAGES_WITH_CONDEMNATION)
            messages_to_return.append(
                condemnation_message.format(self._triplet.word_to_answer)
            )

        if should_the_context_be_returned:
            messages_to_return.extend(context.split("\\n"))
        return messages_to_return

    def send_result(self, messages_to_return) -> None:
        while len(messages_to_return):
            message = messages_to_return.popleft()
            self.send_message(self._chat_id, message)
            time.sleep(HUMANLIKE_PROSSESING_TIME)

    def log_session(self) -> None:
        database_name, table_name = self._log_path.split(".")
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
                asked, answ, right, err, _, debug = self._last_interaction
                self._last_interaction
                keywords: str = ";".join(
                    [
                        ",".join(
                            map(  # TODO: check the following 'x'
                                lambda x: str(
                                    int(x) if isinstance(x, bool) else x
                                ),
                                key_and_value
                            )
                        ) for key_and_value in debug.items()
                    ]
                )
                line = {
                    "timestamp": datetime.datetime.now().timestamp(),
                    "is_the_answer_right": right,
                    "word_to_ask": repr(asked.word_to_ask),
                    "word_to_answer": repr(asked.word_to_answer),
                    "user_answer": repr(answ),
                    "error_message": repr(err),  # TODO: write something
                    "keywords": repr(keywords)
                }
                columns, values = zip(*line.items())
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

    def wait(self) -> None:
        time.sleep(
            self._last_interaction["time_span_before_the_next_interaction"]
        )
