import typing as tp

import numpy as np

from .table_qlearning_agent import TableQLearningAgent


class TimedTableQLearningAgent(TableQLearningAgent):
    def __init__(
            self,
            alpha: float,
            epsilon: float,
            discount: float,
            state_to_legal_actions: tp.Dict[tp.Hashable, tp.Set[tp.Hashable]],
            init_qvalue: float = 0.0,
            softmax_t: float = 1.0,
            waiting_strategy: tp.Tuple[tp.Union[float, tp.Tuple[float, float]], ...] = [0.5]
    ):
        super().__init__(
            alpha=alpha,
            epsilon=epsilon,
            discount=discount,
            state_to_legal_actions=state_to_legal_actions,
            init_qvalue=init_qvalue,
            softmax_t=softmax_t
        )
        self._waiting_strategy = tuple(
            [
                tuple(elem) if isinstance(elem, list) else elem
                    for elem in waiting_strategy
            ]
        )

    def get_action(self, state: tp.Hashable) -> tp.Tuple[tp.Hashable, float]:
        action = super().get_action(state)
        waiting_bounds = self._waiting_strategy[0]
        if isinstance(waiting_bounds, float):
            waiting_time = self._waiting_strategy[0]
        elif isinstance(waiting_bounds, tuple):
            assert len(self._waiting_strategy[0]) == 2
            waiting_time = np.random.randint(*waiting_bounds)
        else:
            raise RuntimeError(
                "Bad type of waiting_strategy element!"
            )
        self._waiting_strategy = (
            *self._waiting_strategy[1:], self._waiting_strategy[0]
        )
        return action, float(waiting_time)

