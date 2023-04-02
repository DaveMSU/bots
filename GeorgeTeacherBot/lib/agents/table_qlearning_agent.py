import typing as tp

import numpy as np

from .base_agent import BaseTableAgent


class TableQLearningAgent(BaseTableAgent):
    def __init__(
            self,
            alpha: float,
            epsilon: float,
            discount: float,
            state_to_legal_actions: tp.Dict[tp.Hashable, tp.Set[tp.Hashable]],
            init_qvalue: float = 0.0,
            softmax_t: float = 1.0
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
            softmax_t=softmax_t
        )
        self.alpha: float = alpha
        self._discount: float = discount

    def update(
            self, 
            state: tp.Hashable, 
            action: tp.Hashable, 
            reward: tp.Union[int, float], 
            next_state: tp.Hashable
        ) -> None:
        """
        You should do your Q-Value update here:
           Q(s,a) := (1 - alpha) * Q(s,a) + alpha * (r + gamma * V(s'))
        """
        curr_qvalue = self._get_qvalue(state, action)
        new_qvalue = reward + self._discount * self._get_value(next_state)
        self._set_qvalue(
            state,
            action,
            curr_qvalue + self.alpha * (new_qvalue - curr_qvalue)
        )

