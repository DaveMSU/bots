import sys; sys.path.append("/home/david_tyuman/telegram_server/bots/GeorgeTeacherBot")  # TODO: remove

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
from lib.types import Triplet


TWO_HOURS = 7200
VALUE_ABSENCE = -1


# TODO: think about whether to move it inside _TripletsHistoryHandler
# TODO: force a blank elem to be a singleton
class _HistoryElement:  
    def __init__(
            self,
            time_interval_to_last: int = VALUE_ABSENCE,
            absolute_time: int = VALUE_ABSENCE,
            was_the_users_answer_right: tp.Union[bool, int] = VALUE_ABSENCE
    ):
        self._time_interval_to_last = time_interval_to_last
        self._absolute_time = absolute_time
        assert int(was_the_users_answer_right) in [VALUE_ABSENCE, 0, 1]
        self._was_the_users_answer_right = was_the_users_answer_right

    @property
    def rel(self) -> int:
        return self._time_interval_to_last

    @property
    def abs(self) -> int:
        return self._absolute_time

    @property
    def is_right(self) -> int:
        return int(self._was_the_users_answer_right)

    def __hash__(self) -> int:
        return hash(
            "".join(
                [
                    str(self._time_interval_to_last),
                    str(self._absolute_time),
                    str(self._was_the_users_answer_right)
                ]
            )
        )

    def __eq__(self, other: '_HistoryElement') -> bool:
        return (self._time_interval_to_last == other.rel)\
            and (self._absolute_time == other.abs)\
            and (self._was_the_users_answer_right == other.is_right)


class _TripletsHistoryHandler:
    def __init__(
            self,
            max_vector_len: int
    ):
        self._max_vector_len = max_vector_len
        self._triplets_history: tp.Dict[
            Triplet, tp.List[_HistoryElement]
        ] = dict()
        
    def __iter__(self):
        return iter(self._triplets_history.keys())

    def get(
            self,
            triplet: Triplet
    ) -> tp.List[_HistoryElement]:
        return self._triplets_history[triplet].copy()
    
    def get_padded(
            self, 
            triplet: Triplet
    ) -> tp.List[_HistoryElement]:
        blank_elem = _HistoryElement()
        history_list = self._triplets_history.get(triplet, [blank_elem])
        if len(history_list) >= self._max_vector_len:
            padded_history = history_list[-self._max_vector_len:]
        else:
            padding = [blank_elem] * (self._max_vector_len - len(history_list))
            padded_history = padding + history_list
        assert len(padded_history) == self._max_vector_len, "Bad pad length."
        return padded_history

    def add(
            self,
            triplet: Triplet,
            timestamp: int,
            is_answer_right: int
    ) -> None:
        if triplet not in self._triplets_history:
            self._triplets_history[triplet] = [
                _HistoryElement(
                    time_interval_to_last=VALUE_ABSENCE,
                    absolute_time=timestamp,
                    was_the_users_answer_right=is_answer_right
                )
            ]
        else:
            prev_item = self._triplets_history[triplet][-1]
            new_item = _HistoryElement(
                time_interval_to_last=timestamp - prev_item.abs,
                absolute_time=timestamp,
                was_the_users_answer_right=is_answer_right
            )
            self._triplets_history[triplet].append(new_item)


def _compute_features(  # TODO: rewrite this method so as to use more info
        padded_history: tp.List[_HistoryElement],
        current_timestamp: int
) -> tp.List[tp.Dict[str, tp.Union[str, int]]]:
    features = list()
    features.append(
        {
            "name": "seconds_from_the_last_interaction",
            "value": VALUE_ABSENCE if padded_history[-1].abs == VALUE_ABSENCE
                else current_timestamp - padded_history[-1].abs
        }
    )
    for i, raw_feature in enumerate(reversed(padded_history)):
        features.append(
            {
                "name": f"is_right_{i}",
                "value": raw_feature.is_right
            }
        )
        features.append(
            {
                "name": f"rel_{i}",
                "value": raw_feature.rel
            }
        )
    return features


class ProbabilisticQLearningWordAgent(BaseTableAgent):
    def __init__(
            self,
            core_parameters: tp.Dict[str, tp.Union[str, tp.Dict[str, tp.Any]]],
            state_to_legal_actions: tp.Dict[
                str,
                tp.Set[Triplet],
            ],
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
        self._triplets_handler = _TripletsHistoryHandler(
            max_vector_len=max_vector_len
        )
        self._data: tp.List[tp.Dict[str, tp.Union[np.ndarray, bool]]] = list()
        self._next_interaction_timestamp: int = round(time.time())
        if len(self._state_to_legal_actions) > 1:
            raise RuntimeError(
                "Dict state_to_legal_actions"
                " has more than 1 key what is denied!"
            )
        self._main_state: str = next(iter(self._state_to_legal_actions.keys()))
        
    def _get_how_long_to_wait(self) -> int:
        return max(0, self._next_interaction_timestamp - round(time.time()))

    def update(
            self, 
            state: str,
            action: Triplet,
            reward: tp.Union[int, float], 
            next_state: str,
            extra_params: tp.Optional[tp.Dict[str, tp.Any]] = None
    ) -> None:
        """
        """
        is_it_a_pretrain_step: bool = extra_params["is_it_a_pretrain_step"]
        action_timestamp: int = extra_params["timestamp"]
        assert int(reward) in [0, 1]
        padded_word_history_for_the_current_one = \
            self._triplets_handler.get_padded(action)
        self._data.append(
            {
                "features": _compute_features(
                    padded_word_history_for_the_current_one,
                    action_timestamp
                ),
                "target": int(reward)
            }
        )

        if not is_it_a_pretrain_step:
            X = np.array(
                [
                    [feature["value"] for feature in data_line["features"]]
                    for data_line in self._data  
                ]
            )
            y = np.array([data_line["target"] for data_line in self._data])            
            self._core_ml_model.fit(X, y)
            X, y = None, None  # clearing the RAM

        self._triplets_handler.add(
            triplet=action,
            timestamp=action_timestamp,
            is_answer_right=int(reward)
        )

        if not is_it_a_pretrain_step:
            wait_for: int = 0
            state_to_legal_actions = self._state_to_legal_actions[self._main_state]
            while True:
                current_timestamp=round(time.time())
                triplet_to_features: tp.Dict[str, tp.List[int]] = OrderedDict(
                    (
                        triplet,
                        [
                            feature["value"] for feature in _compute_features(
                                padded_history=self._triplets_handler.get_padded(triplet),
                                current_timestamp=current_timestamp + wait_for
                            )
                        ]
                    ) for triplet in state_to_legal_actions
                )
            
                X = np.array(list(triplet_to_features.values()))
                # y_prob - probability of the target being equals to 1.0
                y_prob = self._core_ml_model.predict_proba(X)[:, 1] 
                indexes = np.argsort(y_prob)
                
                if np.max(y_prob) < self._knowledge_threshold and wait_for < TWO_HOURS:
                    wait_for = wait_for + np.random.randint(1, 20)
                    continue
                for i, triplet in enumerate(triplet_to_features):
                    # TODO: check, why here is no 1.0 - p
                    self._set_qvalue(state, triplet, y_prob[i])
                break  # TODO: remove this line
            self._next_interaction_timestamp = current_timestamp + wait_for

