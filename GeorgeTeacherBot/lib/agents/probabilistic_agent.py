import datetime
import typing as tp

import numpy as np
from sklearn.ensemble import (
    ExtraTreesClassifier,
    RandomForestClassifier
)
from sklearn.neural_network import MLPClassifier

from .base_agent import BaseTableAgent


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
        blank_elem = {key: -1 for key in self._item_temlpate}  # TODO: global
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
                    "rel": -1,
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

    def add_get_padded(
            self,
            word: str,
            timestamp: int,
            is_answer_right: int
    ) -> tp.List[tp.Dict[str, int]]:
        if word not in self._words_history:
            hypothetical_word_history = [
                {
                    "rel": -1,
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
            hypothetical_word_history = self._words_history[word] + [new_item]
        blank_elem = {key: -1 for key in self._item_temlpate}
        if len(hypothetical_word_history) >= self._max_vector_len:
            padded_history = hypothetical_word_history[-self._max_vector_len:]
        else:
            padding = [blank_elem] * (self._max_vector_len - len(hypothetical_word_history))
            padded_history = padding + hypothetical_word_history
        return padded_history
        

def _compute_features(
        padded_history: tp.List[tp.Dict[str, int]]
) -> tp.Dict[int, tp.Dict[str, tp.Union[str, int]]]:
    features = dict()
    cnt = 0
    for i, row_feature in enumerate(reversed(padded_history)):
        features[cnt] = {
            "name": f"is_right_{i}",
            "value": row_feature["is_right"]
        }
        cnt += 1
        features[cnt] = {
            "name": f"rel_{i}",
            "value": row_feature["rel"]
        }
        cnt += 1
    return features


class ProbabilisticQLearningAgent(BaseTableAgent):
    def __init__(
            self,
            state_to_legal_actions: tp.Dict[tp.Hashable, tp.Set[tp.Hashable]],
            training_frequency: int = 2,  # TODO: increase
            max_vector_len: int = 2,  # TODO: increase
            init_qvalue: float = 0.0,
            softmax_t: float = 1.0,
            waiting_strategy: tp.Tuple[
                tp.Union[float, tp.Tuple[float, float]], ...
            ] = (0.5,)
    ):
        """
        """
        super().__init__(
            state_to_legal_actions=state_to_legal_actions,
            init_qvalue=init_qvalue,
            epsilon=0.0,
            softmax_t=softmax_t,
            waiting_strategy=waiting_strategy
        )
        self._interactions_without_training: int = training_frequency
        self._training_frequency = training_frequency
        self._words_handler = _WordsHistoryHandler(
            max_vector_len=max_vector_len
        )
        self._data: tp.List[tp.Dict[str, tp.Union[np.ndarray, bool]]] = list()
        self._core_ml_model = RandomForestClassifier()  # TODO: add parameter passing.
        # self._core_ml_model = ExtraTreesClassifier()  # MLPClassifier()

    def update(  # TODO: this code includes error - no timestamp support.
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
        self._words_handler.add(
            word=action,
            timestamp=action_timestamp,
            is_answer_right=int(reward)  # TODO: seems like here is a mistake - like we put target through training example.
        )
        padded_word_history_for_the_current_one = \
            self._words_handler.get_padded(action)
        self._data.append(
            {
                "features": _compute_features(
                    padded_word_history_for_the_current_one
                ),
                "target": int(reward)
            }
        )
        print(len(self._data))

        # if (not is_it_pretrain_step) or (self._interactions_without_training == self._training_frequency):
        if not is_it_pretrain_step:
            self._interactions_without_training = 0
            X = np.array(
                [
                    [feature["value"] for feature in data_line["features"].values()]
                    for data_line in self._data  
                ]
            )
            y = np.array([data_line["target"] for data_line in self._data])            
            self._core_ml_model.fit(X, y)
            print(X.shape)
            X, y = None, None

        if not is_it_pretrain_step:
            for word in self._words_handler:
                features = _compute_features(
                    self._words_handler.add_get_padded(
                        word=word,
                        timestamp=datetime.datetime.now().timestamp(),
                        is_answer_right=0  # TODO: something wrong because of this.
                    )
                )
                x = np.array([feature["value"] for feature in features.values()])
                y_prob = 1.0 - self._core_ml_model.predict_proba(x[np.newaxis, :])[0, 0]       
                self._set_qvalue(state, word, y_prob)
                print(word, y_prob, end="  ")
            print()
        # self._interactions_without_training += 1

