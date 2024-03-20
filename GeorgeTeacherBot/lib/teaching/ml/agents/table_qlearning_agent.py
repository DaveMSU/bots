import typing as tp

import numpy as np

from .base_agent import BaseTableAgent
from lib.types import Triplet


class TableQLearningAgent(BaseTableAgent):
    def __init__(
            self,
            alpha: float,
            epsilon: float,
            discount: float,
            state_to_legal_actions: tp.Dict[str, tp.Set[Triplet]],
            init_qvalue: float = 0.0,
            softmax_t: float = 1.0,
            waiting_strategy: tp.Tuple[  # TODO: fix typing
                tp.Union[float, tp.Tuple[float, float]], ...
            ] = (0.5,)
    ):
        """
        Q-Learning Agent
        based on https://inst.eecs.berkeley.edu/~cs188/sp19/projects.html
        Instance variables you have access to
          - self.epsilon (exploration prob)
          - self.alpha (learning rate)
          - self._discount (discount rate aka gamma)

        Functions you should use
          - self.get_action(state)
          - self.update(...)
          - self.rewrite_states_and_actions(new_state_to_legal_actions)
        """
        super().__init__(
            state_to_legal_actions=state_to_legal_actions,
            init_qvalue=init_qvalue,
            epsilon=epsilon,
            softmax_t=softmax_t,
        )
        self.alpha: float = alpha
        self._discount: float = discount
        self._waiting_strategy = waiting_strategy  # TODO: fix typing.

    def _get_how_long_to_wait(self) -> float:
        waiting_bounds = self._waiting_strategy[0]
        if isinstance(waiting_bounds, float):
            waiting_time = self._waiting_strategy[0]
        elif isinstance(waiting_bounds, list):  # TODO: fix typing
            waiting_time = np.random.randint(*waiting_bounds)
        else:
            raise RuntimeError(
                "Bad type of 'waiting_strategy' variable!"
                f" Type `{type(waiting_bounds)}` was found,"
                " but `float` or `list` were expected."
            )
        self._waiting_strategy = (
            *self._waiting_strategy[1:], self._waiting_strategy[0]
        )
        return float(waiting_time)

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
        You should do your Q-Value update here:
           Q(s,a) := (1 - alpha) * Q(s,a) + alpha * (r + gamma * V(s'))
        """
        for seq_portion in sequence:
            state: str = seq_portion["state"]
            action: tp.Tuple[Triplet, int] = seq_portion["action"]
            reward: tp.Union[int, float] = seq_portion["reward"]
            next_state: str = seq_portion["next_state"]
            
            curr_qvalue = self._get_qvalue(state, action[0])
            new_qvalue = reward + self._discount * self._get_value(next_state)
            self._set_qvalue(
                state,
                action,
                curr_qvalue + self.alpha * (new_qvalue - curr_qvalue)
            )
