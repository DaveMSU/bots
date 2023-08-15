import datetime
import time
import typing as tp
from collections import OrderedDict

import numpy as np
from sklearn.ensemble import (
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier
)
from sklearn.neural_network import MLPClassifier

from .base_agent import BaseTableAgent


TWO_HOURS = 7200
VALUE_ABSENCE = -1


class _WordsHistoryHandler:
    def __init__(
            self,
            max_vector_len: int
    ):
        self._max_vector_len = max_vector_len
        self._words_history: tp.Dict[str, tp.List[tp.Dict[str, int]]] = dict()
        self._item_temlpate = {"rel": int, "abs": int, "is_right": int}
        
    def __iter__(self):
        return iter(self._words_history.keys())

    def get(
            self, 
            word: str
    ) -> tp.Dict[str, tp.List[tp.Dict[str, int]]]:
        return self._words_history[word].copy()
    
    def get_padded(
            self, 
            word: str
    ) -> tp.List[tp.Dict[str, int]]:
        blank_elem = {key: VALUE_ABSENCE for key in self._item_temlpate}  # TODO: global
        history_list = self._words_history.get(word, [blank_elem])
        if len(history_list) >= self._max_vector_len:
            padded_history = history_list[-self._max_vector_len:]
        else:
            padding = [blank_elem] * (self._max_vector_len - len(history_list))
            padded_history = padding + history_list
        return padded_history

    def add(
            self,
            word: str,
            timestamp: int,
            is_answer_right: int
    ) -> None:
        if word not in self._words_history:
            self._words_history[word] = [
                {
                    "rel": VALUE_ABSENCE,
                    "abs": timestamp,
                    "is_right": is_answer_right
                }
            ]
        else:
            prev_item = self._words_history[word][-1]
            new_item = {   
                "rel": timestamp - prev_item["abs"],
                "abs": timestamp,
                "is_right": is_answer_right
            }
            self._words_history[word].append(new_item)


def _compute_features(
        padded_history: tp.List[tp.Dict[str, int]],
        current_timestamp: int
) -> tp.List[tp.Dict[str, tp.Union[str, int]]]:
    features = list()
    features.append(
        {
            "name": "seconds_from_the_last_interaction",
            "value": VALUE_ABSENCE if padded_history[-1]["abs"] == VALUE_ABSENCE
                else current_timestamp - padded_history[-1]["abs"]
        }
    )
    for i, row_feature in enumerate(reversed(padded_history)):
        features.append(
            {
                "name": f"is_right_{i}",
                "value": row_feature["is_right"]
            }
        )
        features.append(
            {
                "name": f"rel_{i}",
                "value": row_feature["rel"]
            }
        )
    return features


class ProbabilisticQLearningWordAgent(BaseTableAgent):
    def __init__(
            self,
            core_parameters: tp.Dict[str, tp.Union[str, tp.Dict[str, tp.Any]]],
            state_to_legal_actions: tp.Dict[tp.Hashable, tp.Set[tp.Hashable]],
            knowledge_threshold: float = 0.5,
            epsilon: float = 0.1,
            max_vector_len: int = 5,
            init_qvalue: float = 0.01,
            softmax_t: float = 1.0
    ):
        """
        """
        super().__init__(
            state_to_legal_actions=state_to_legal_actions,
            init_qvalue=init_qvalue,
            epsilon=epsilon,
            softmax_t=softmax_t
        )
        self._core_ml_model = globals()[
            core_parameters["model_type"]
        ](
            **core_parameters["params"]
        )
        self._knowledge_threshold: float = knowledge_threshold
        self._words_handler = _WordsHistoryHandler(
            max_vector_len=max_vector_len
        )
        self._data: tp.List[tp.Dict[str, tp.Union[np.ndarray, bool]]] = list()
        self._next_interaction_timestamp: int = round(time.time())
        if len(self._state_to_legal_actions) > 1:
            raise RuntimeError(
                "Dict state_to_legal_actions"
                " has more than 1 key which is denied!"
            )
        self._main_state: str = next(iter(self._state_to_legal_actions.keys()))
        

    def _get_how_long_to_wait(self) -> int:
        return max(0, self._next_interaction_timestamp - round(time.time()))

    def update(
            self, 
            state: str,
            action: str,
            reward: tp.Union[int, float], 
            next_state: str,
            extra_params: tp.Optional[tp.Dict[str, tp.Any]] = None
    ) -> None:
        """
        """
        is_it_pretrain_step: bool = extra_params["is_it_pretrain_step"]
        action_timestamp: int = extra_params["timestamp"]
        assert int(reward) in [0, 1]
        padded_word_history_for_the_current_one = \
            self._words_handler.get_padded(action)
        self._data.append(
            {
                "features": _compute_features(
                    padded_word_history_for_the_current_one,
                    action_timestamp
                ),
                "target": int(reward)
            }
        )

        if not is_it_pretrain_step:
            X = np.array(
                [
                    [feature["value"] for feature in data_line["features"]]
                    for data_line in self._data  
                ]
            )
            y = np.array([data_line["target"] for data_line in self._data])            
            self._core_ml_model.fit(X, y)
            X, y = None, None

        self._words_handler.add(
            word=action,
            timestamp=action_timestamp,
            is_answer_right=int(reward)
        )

        if not is_it_pretrain_step:
            wait_for = 0
            while True:
                current_timestamp=round(time.time())
                word_to_features: tp.Dict[str, tp.List[int]] = OrderedDict(
                    {
                        word: [
                            feature["value"] for feature in _compute_features(
                                padded_history=self._words_handler.get_padded(word),
                                current_timestamp=current_timestamp + wait_for
                            )
                        ] for word in self._state_to_legal_actions[self._main_state]
                    }
                )
            
                X = np.array(list(word_to_features.values()))
                y_prob = self._core_ml_model.predict_proba(X)[:, 1]  # probability of target = 1
                indexes = np.argsort(y_prob)
                if np.max(y_prob) < self._knowledge_threshold and wait_for < TWO_HOURS:
                    wait_for = wait_for + np.random.randint(1, 20)
                    continue
                l = []
                for i, word in enumerate(word_to_features):
                    self._set_qvalue(state, word, y_prob[i])  # TODO: check, why here is no 1.0 - p
                    l.append((word, y_prob[i]))
                break
            self._next_interaction_timestamp = current_timestamp + wait_for

