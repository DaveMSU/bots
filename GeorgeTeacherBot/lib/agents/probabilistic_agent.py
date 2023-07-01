import typing as tp

import numpy as np

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
        blank_elem = {key: -1 for key in self._item_temlpate}
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
            raw_item: tp.Dict[str, tp.Any]
    ) -> None:
        if word not in self._words_history:
            self._words_history[word] = [
                {
                    "rel": -1,
                    "abs": raw_item["timestamp"],
                    "is_right": raw_item["is_answer_right"]
                }
            ]
        else:
            prev_item = self._words_history[word][-1]
            new_item = {   
                "rel": raw_item["timestamp"] - prev_item["abs"],
                "abs": raw_item["timestamp"],
                "is_right": raw_item["is_answer_right"]
            }
            self._words_history[word].append(new_item)


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
            training_frequency: int = 2,  # TODO: increase
            max_vector_len: int = 2,  # TODO: increase
            state_to_legal_actions: tp.Dict[tp.Hashable, tp.Set[tp.Hashable]],
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
            epsilon=epsilon,
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

    def update(  # TODO: this code include error - no timestamp support.
            self, 
            state: str,
            action: str,
            reward: tp.Union[int, float], 
            next_state: str
        ) -> None:
        """
        """
        padded_word_history_for_the_current_one = \
            self._words_handler.get_padded(action)
        features = _compute_features(padded_word_history_for_the_current_one)
        target = int(reward)
        assert target in [0, 1]
        self._data.append(
            {
                "features": features,
                "target": target
            }
        )
        if self._interactions_without_learning == self._training_frequency:
            self._interactions_without_learning = 0
            X = np.array(
                [
                    [feature["value"] for feature in data_line["features"].values()]
                    for data_line in prepared_data  
                ]
            )
            y = np.array([data_line["target"] for data_line in prepared_data])            
            model = RandomForestClassifier()
            self._core_ml_model.fit(X_train, y_train)
            X, y = None, None

        for word in self._words_handler:
            features = _compute_features(
                self._words_handler.get_padded(word)
            )
            x = np.array([feature["value"] for feature in features])
            y_prob = model.predict_proba(x[np.newaxis, :])[0, 1]        
            self._set_qvalue(state, word, y_prob)

        self._interactions_without_learning -= 1

