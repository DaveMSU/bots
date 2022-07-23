import sys; sys.path.append("/home/david_tyuman/telegram_server/bots")
import datetime
import logging
import re
import time
import typing as tp
from collections import deque

import numpy as np

from global_vars import (
    MESSAGES_WITH_PRAISE, 
    MESSAGES_WITH_CONDEMNATION,
    change_layout
)
from TableQLearningAgent import QLearningAgent
from telegrambot import TelegramBot

LANGUAGES = ["eng_word", "rus_word"]
TIME_TO_WAIT = 0.1
HUMANLIKE_PROSSESING_TIME = 1.0
MAIN_STATE = "main_state"


class GeorgeBot(TelegramBot):
    KEYS = ["eng_word", "rus_word", "comment"]

    def __init__(
            self,
            token: str, 
            chat_id: int,
            path_to_base: str,
            *,
            chat_logger: logging.Logger,
            ml_logger: logging.Logger,
            alpha: float,
            epsilon: float,
            discount: float,
            init_qvalue: float,
            softmax_t: float
        ):
        TelegramBot.__init__(self, token)  # TODO: use super().
        self._chat_id: int = chat_id
        self._path_to_base: str = path_to_base
        self._base: tp.Dict[str, tp.Dict[str, str]] = dict()
        # self._probs: np.array = np.array([1.0])
        self._triplet: tp.Optional[tp.Dict[str, str]] = None
        self._user_answer: str = ""
        self._return_comment: tp.Optional[bool] = None
        self._error_message: str = ""
        self._messages_to_return: tp.Deque[str] = deque()
        self._loggers: tp.Dict[str, tp.Any] = {
            "chat_logger": chat_logger,
            "ml_logger": ml_logger
        }

        self.load_words()
        state_to_legal_actions = {MAIN_STATE: set(self._base)}
        self._agent = QLearningAgent(  # TODO: use super().
            alpha,
            epsilon,
            discount,
            state_to_legal_actions,
            init_qvalue,
            softmax_t
        )

    def load_words(
            self, 
            path: tp.Optional[str] = None
        ) -> None:
        """
        :param path: path to txt file with base of words.
        Construct self._base atribute that have 
         next type: tp.Dict[str, tp.Dict[str, str]].
        """
        path = self._path_to_base if path is None else path
        parsed_words_base: tp.Dict[str, tp.Dict[str, str]] = dict()
        with open(path, 'r') as f:
            for line in f:
                line_parts = list(map(lambda x: x.strip(), re.split(" - | #", line)))
                if "#" not in line:            
                    line_parts.append("Sorry, no using example.")
#                 assert len(line_parts) == 3, (
#                     f"len(line_parts+ must be = 3, but {len(line_parts)}"
#                     f" occured!\nline_parts = {line_parts}"
#                 )
                for i in [0, 1]:
                    triplet = {
                        "word_to_ask": line_parts[i], 
                        "word_to_answer": line_parts[i ^ 1],
                        "comment": " - ".join(line_parts[2:]).strip()  # TODO
                    }
                    parsed_words_base.update({line_parts[i]: triplet})
        self._base = parsed_words_base
        
    def update_base(self) -> tp.List[tp.Dict[str, str]]:
        self.load_words()
        self._agent.change_state_to_legal_actions(
            {MAIN_STATE: set(self._base)}
        )

    def _choose_triplet(self, base: tp.List[tp.Any]) -> tp.Dict[str, str]:
        word_to_ask = self._agent.get_action(MAIN_STATE)
        self._triplet = self._base[word_to_ask]
    
    def ask_word(self) -> None:
        self._choose_triplet(self._base)
        self.send_message(self._chat_id, self._triplet["word_to_ask"])
   
    def wait_for_an_message(self) -> None:
        while True:
            self.wait(TIME_TO_WAIT)
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
    def _check_words_similarity(s1: str, s2: str) -> bool:
        lev_dist = min(
            GeorgeBot._lev_dist(s1.lower(), s2.lower()),
            GeorgeBot._lev_dist(change_layout(s1.lower()), s2.lower()) + 1
        )
        return lev_dist <= 1

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
            
        self._return_comment = (parts[-1] == 'c')
        self._is_answer_right = self._check_words_similarity(
            self._triplet["word_to_answer"],
            parts[0]
        )

        if self._is_answer_right:
            praise_message = np.random.choice(MESSAGES_WITH_PRAISE)
            self._messages_to_return.append(praise_message)
        else:
            condemnation_message = np.random.choice(MESSAGES_WITH_CONDEMNATION)
            self._messages_to_return.append(
                condemnation_message.format(self._triplet["word_to_answer"])
            )

        if self._return_comment:
            self._messages_to_return.append(self._triplet["comment"])

        self._agent.update(
            state=MAIN_STATE,
            action=self._triplet["word_to_ask"],
            reward=float(not self._is_answer_right),
            next_state=MAIN_STATE
        )

    def send_result(self) -> None:
        while len(self._messages_to_return):
            message = self._messages_to_return.popleft()
            self.send_message(self._chat_id, message)
            self.wait(HUMANLIKE_PROSSESING_TIME)

    def parse_log(
            self, 
            log_path: str
        ) -> tp.List[tp.Dict[str, tp.Union[str, bool]]]:
        """
        :param log_path: path to log of chat.
        :return: [
            {
                'date': datetime.datetime,
                'timestamp': float,
                'is_answer_right': bool,
                'word_to_ask': str,
                'word_to_answer': str,
                'user_answer': str,
                'error_message': str
            },
            ...
        ]
        """
        parsed_log: tp.List[tp.Dict[str, tp.Union[str, bool]]] = []
        with open(log_path, 'r') as f:
            for line in f:
                line_parts = line.rstrip().split(' - ')
                date = datetime.datetime.strptime(
                    line_parts[0], "%Y-%m-%d %H:%M:%S,%f"
                )
                parsed_line = {
                        'date': date,
                        'timestamp': time.mktime(date.timetuple()),
                        'is_answer_right': line_parts[3].split("=")[1] == "True",
                        'word_to_ask': line_parts[4].split("=")[1][1:-1],
                        'word_to_answer': line_parts[5].split("=")[1][1:-1],
                        'user_answer': line_parts[6].split("=")[1][1:-1].split("_")[0],
                        'error_message': line_parts[7].split("=")[1].replace("'", "")
                }
                parsed_log.append(parsed_line)
        return parsed_log

    def pretrain(self, log_path: str) -> None:
        parsed_log = self.parse_log(log_path)
        for record in parsed_log:
            self._agent.update(
                state=MAIN_STATE,
                action=record["word_to_ask"],
                reward=float(not record["is_answer_right"]),
                next_state=MAIN_STATE
            )

    @staticmethod
    def wait(seconds: int) -> None:
        time.sleep(seconds)

    def log_session(self) -> None:
        log_line = (
            f"is_answer_right={self._is_answer_right} - "
            f"word_to_ask={repr(self._triplet['word_to_ask'])} - "
            f"word_to_answer={repr(self._triplet['word_to_answer'])} - "
            f"user_answer={repr(self._user_answer)} - "
            f"error_message={repr(self._error_message)}"
        )
        self._loggers["chat_logger"].debug(log_line)

        pre_log_line = [
            {
                "state": repr(state),
                "action": repr(action),
                "qvalue": self._agent.get_qvalue(state, action)
            }
            for state in self._agent._state_to_legal_actions
                for action in self._agent._state_to_legal_actions[state] 
        ]
        pre_log_line = sorted(pre_log_line, key=lambda x: x["qvalue"])

        log_line = " - ".join(
            [
                f"Q({line['state']}, {line['action']})={line['qvalue']}"
                    for line in pre_log_line
            ]
        )

        self._loggers["ml_logger"].debug(log_line)

