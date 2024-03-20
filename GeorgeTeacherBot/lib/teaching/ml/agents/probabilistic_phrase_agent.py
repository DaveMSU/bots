import sys; sys.path.append("/home/david_tyuman/telegram_server/bots/GeorgeTeacherBot")  # TODO: remove

import datetime
import time
import typing as tp
from collections import OrderedDict

import numpy as np
# TODO: create models.py and move all models there to avoid F401
from sklearn.ensemble import (
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier
)
from sklearn.neural_network import MLPClassifier

from .base_agent import BaseTableAgent
from lib.types import Triplet


TWO_HOURS: int = 720
VALUE_ABSENCE: int = -1


# TODO: think about whether to move it inside ot the TripletHistoryHandler
# TODO: force a blank elem to be a singleton, or something similar.
class HistoryElement:
    def __init__(
            self,
            time_interval_to_the_last: int = VALUE_ABSENCE,
            absolute_time: int = VALUE_ABSENCE,
            was_the_users_answer_right: tp.Union[bool, int] = VALUE_ABSENCE,
    ):
        self._time_interval_to_the_last = time_interval_to_the_last
        self._absolute_time = absolute_time
        assert int(was_the_users_answer_right) in [VALUE_ABSENCE, 0, 1]
        self._was_the_users_answer_right = was_the_users_answer_right

    @property
    def rel(self) -> int:
        return self._time_interval_to_the_last

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
                    str(self._time_interval_to_the_last),
                    str(self._absolute_time),
                    str(self._was_the_users_answer_right),
                ]
            )
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return (self._time_interval_to_the_last == other.rel)\
                and (self._absolute_time == other.abs)\
                and (self._was_the_users_answer_right == other.is_right)
        else:
            return False


class TripletHistoryHandler:
    def __init__(
            self,
            max_vector_len: int,
    ):
        self._max_vector_len = max_vector_len
        self._triplets_history: tp.Dict[
            Triplet, tp.List[HistoryElement]
        ] = dict()

    def __iter__(self):
        return iter(self._triplets_history.keys())

    def get(
            self,
            triplet: Triplet,
    ) -> tp.List[HistoryElement]:
        return self._triplets_history[triplet].copy()

    def get_padded(
            self,
            triplet: Triplet,
    ) -> tp.List[HistoryElement]:
        blank_elem = HistoryElement()
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
            is_answer_right: int,
    ) -> None:
        if triplet not in self._triplets_history:
            self._triplets_history[triplet] = [
                HistoryElement(
                    time_interval_to_the_last=VALUE_ABSENCE,
                    absolute_time=timestamp,
                    was_the_users_answer_right=is_answer_right
                )
            ]
        else:
            prev_item = self._triplets_history[triplet][-1]
            new_item = HistoryElement(
                time_interval_to_the_last=timestamp - prev_item.abs,
                absolute_time=timestamp,
                was_the_users_answer_right=is_answer_right
            )
            self._triplets_history[triplet].append(new_item)


def compute_features(  # TODO: rewrite this method so as to use more info
        padded_history: tp.List[HistoryElement],
        current_timestamp: int,
) -> tp.List[tp.Dict[str, tp.Union[str, int]]]:
    features = list()
    features.append(
        {
            "name": "second_from_the_last_interaction",
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


class ProbabilisticQLearningPhraseAgent(BaseTableAgent):
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
            softmax_t: float = 1.0,
    ):
        """
        TODO: write a description.
        """
        super().__init__(
            state_to_legal_actions=state_to_legal_actions,
            init_qvalue=init_qvalue,
            epsilon=epsilon,
            softmax_t=softmax_t,
        )
        self.CNT = 0  # TODO: rm
        self._core_ml_model = globals()[
            core_parameters["model_type"]
        ](
            **core_parameters["params"]
        )
        self._knowledge_threshold: float = knowledge_threshold
        self._triplet_handler = TripletHistoryHandler(
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

    def _process_one_action(
            self,
            state: str,
            action: tp.Tuple[Triplet, int],
            reward: tp.Union[int, float],
            next_state: str,
    ) -> None:
        triplet, action_timestamp = action
        assert int(reward) in [0, 1]
        padded_phrase_history_for_the_current_one: tp.List[HistoryElement] = \
            self._triplet_handler.get_padded(triplet)
        self._data.append(
            {
                "features": compute_features(
                    padded_phrase_history_for_the_current_one,
                    action_timestamp
                ),
                "target": int(reward)
            }
        )
        self._triplet_handler.add(
            triplet=triplet,
            timestamp=action_timestamp,
            is_answer_right=int(reward)
        )
        print(self.CNT)  # TODO: rm
        self.CNT += 1  # TODO: rm

    def _train_on_the_data_and_infer_probabilities(self, state: str) -> None:
        print("train function has started!")  # TODO: rm
        X = np.array(
            [
                [feature["value"] for feature in data_line["features"]]
                for data_line in self._data
            ]
        )
        y = np.array([data_line["target"] for data_line in self._data])
        
        print(f"before fit method (time.time())")  # TODO: rm
        self._core_ml_model.fit(X, y)
        print(f"after fit method (time.time())")  # TODO: rm
        X, y = None, None  # clearing the RAM

        wait_for: int = 0
        state_to_legal_actions = self._state_to_legal_actions[
            self._main_state
        ]
        while True:
            print("while has started!")  # TODO: rm
            current_timestamp: int = round(time.time())
            triplet_to_features: tp.Dict[str, tp.List[int]] = OrderedDict(
                (
                    triplet,
                    [
                        feature["value"] for feature in compute_features(
                            padded_history=self._triplet_handler.get_padded(triplet),
                            current_timestamp=current_timestamp + wait_for
                        )
                    ]
                ) for triplet in state_to_legal_actions
            )
            
            X = np.array(list(triplet_to_features.values()))
            print(f"X.shape = {X.shape}")  # TODO: rm
            # y_prob - that the target will be equal to 1.0
            y_prob = 1 - self._core_ml_model.predict_proba(X)[:, 0]
            print(f"{y_prob.max()=}")  # TODO: rm
            print(f"{y_prob.min()=}")  # TODO: rm
            print(f"{y_prob.mean()=}")  # TODO: rm
            print(f"{y_prob.std()=}")  # TODO: rm
            print(f"{wait_for=}")  # TODO: rm
            if (np.max(y_prob) < self._knowledge_threshold
                    and wait_for < TWO_HOURS):
                wait_for = wait_for + np.random.randint(1, 20)
                continue
            for i, triplet in enumerate(triplet_to_features):
                # TODO: check, why here is no 1.0 - p
                self._set_qvalue(state, triplet, y_prob[i])
            break  # TODO: find a way to remove this line
            self._next_interaction_timestamp = current_timestamp + wait_for
            print("while has finished!")  # TODO: rm
        print("train function has finished!")  # TODO: rm
        
    def update(
            self,
            sequence: tp.List[
                tp.Dict[
                    str,
                    tp.Union[
                        str,
                        tp.Tuple[Triplet, int],
                        tp.Union[int, float]
                    ]
                ]
            ],
    ) -> None:
        """
        action - tuple of triplet and timestamp
        """
        for seq_portion in sequence:
            self._process_one_action(**seq_portion)
        else:
            self._train_on_the_data_and_infer_probabilities(
                state=seq_portion["state"]
            )
