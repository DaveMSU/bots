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
from lib.teaching import ForeignLanguageTeacher
from lib.types import Triplet
from telegrambot import TelegramBot


TIME_TO_WAIT: float = 0.001
HUMANLIKE_PROSSESING_TIME: float = 0.01


class GeorgeBot(TelegramBot):
    def __init__(
            self,
            token: str,
            db_password: str,
            chat_id: int,
            teachers_config: tp.Dict[str, tp.Union[str, dict]],
            path_to_the_log_file: str,
    ):
        TelegramBot.__init__(self, token)  # TODO: use super().
        self._db_password = db_password
        self._chat_id: int = chat_id
        self._teacher = ForeignLanguageTeacher(**teachers_config)
        self._log_path: str = path_to_the_log_file
        print(1)

    def conduct_one_session_with_the_student(self) -> None:
        asked_triplet: Triplet
        waiting_time: float
        debug_info: tp.Dict[str, tp.Any]
        asked_triplet, waiting_time, debug_info = self._ask_a_phrase()

        message: str = self._wait_for_a_message()

        result: tp.List[str]
        is_the_answer_right: bool
        error: str
        result, is_the_answer_right, error = self._process_the_interaction(
            teachers_question=asked_triplet,
            students_answer=message
        )

        self._send_a_result_to_the_student(result)
        self._update_the_teacher()
        self._log_a_session(
            asked=asked_triplet,
            answ=message,
            right=is_the_answer_right,
            err=error,
            debug=debug_info,
        )
        self._wait(waiting_time)

    def _ask_a_phrase(self) -> tp.Tuple[Triplet, float, tp.Dict[str, tp.Any]]:
        triplet, waiting_time, debug_info = self._teacher.ask()
        self.send_message(self._chat_id, triplet.phrase_to_ask)
        return triplet, waiting_time, debug_info

    def _wait_for_a_message(self) -> str:
        while True:
            time.sleep(TIME_TO_WAIT)
            message_data = self.look_for_new_message()
            if message_data:
                break
        assert isinstance(message_data, dict)
        return message_data["message"]["text"]

    def _process_the_interaction(  # TODO: rewrite this func
            self,
            teachers_question: Triplet,
            students_answer: str,
    ) -> tp.Tuple[tp.List[str], bool, str]:
        error_message: str = ""
        messages_to_return: tp.List[str] = []

        # TODO: create specific class for the message
        parts = list(map(lambda x: x.strip(), students_answer.split('_')))
        if len(parts) > 2:
            error_message = (
                "Sorry, but you can enter a maximum of 2 words separated by"
                f" underscores! But you entered {len(parts)} words!"
            )
            messages_to_return.append(error_message)
            return messages_to_return

        if len(parts) == 2 and parts[-1] != 'c':
            error_message = (
                "Sorry, but you entered an undefined identifier!\n"
                "At the moment I can only understand the id \'c\',"
                f" but \'{parts[-1]}\' has been received!"
            )
            messages_to_return.append(error_message)
            return messages_to_return

        should_the_context_be_returned: bool  = (parts[-1] == 'c')

        is_right: bool = self._teacher.process_a_question_and_an_answer(
            question=teachers_question,
            answer=parts[0],
        )
        if is_right:
            praise_message = np.random.choice(MESSAGES_WITH_PRAISE)
            messages_to_return.append(praise_message)
        else:
            condemnation_message = np.random.choice(MESSAGES_WITH_CONDEMNATION)
            messages_to_return.append(
                condemnation_message.format(teachers_question.phrase_to_answer)
            )

        if should_the_context_be_returned:
            messages_to_return.extend(teachers_question.context.split("\\n"))
        return messages_to_return, is_right, error_message

    def _send_a_result_to_the_student(self, messages_to_return: tp.List[str]) -> None:
        while len(messages_to_return):
            message: str = messages_to_return.pop()
            self.send_message(self._chat_id, message)
            time.sleep(HUMANLIKE_PROSSESING_TIME)

    def _update_the_teacher(self) -> None:
        self._teacher.check_if_a_new_trained_brain_has_appeared_and_load_it()

    def _log_a_session(
            self,
            asked: Triplet,
            answ: str,
            right: bool,
            err: str,
            debug: dict,
    ) -> None:
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
                    "phrase_to_ask": repr(asked.phrase_to_ask),
                    "phrase_to_answer": repr(asked.phrase_to_answer),
                    "users_answer": repr(answ),
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

    def _wait(self, seconds: float) -> None:
        time.sleep(seconds)
