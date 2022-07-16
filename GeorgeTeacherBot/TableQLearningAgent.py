import typing as tp
from collections import defaultdict

import numpy as np


class QLearningAgent:
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
          - self.get_legal_actions(state) {state, hashable -> list of actions, each is hashable}
            which returns legal actions for a state
          - self.get_qvalue(state,action)
            which returns Q(state,action)
          - self.set_qvalue(state,action,value)
            which sets Q(state,action) := value
        !!!Important!!!
        Note: please avoid using self._qValues directly.
            There's a special self.get_qvalue/set_qvalue for that.
        """
        self._softmax_t = softmax_t
        self._init_qvalue = init_qvalue
        self._state_to_legal_actions: tp.Dict[tp.Hashable, tp.Set[tp.Hashable]] =\
            state_to_legal_actions
        self._qvalues: tp.Dict[tp.Hashable, tp.Dict[tp.Hashable, float]] = {
            state: {
                action: self._init_qvalue for action in state_to_legal_actions[state]
            } for state in state_to_legal_actions
        }
        self.alpha: float = alpha
        self.epsilon: float = epsilon
        self._discount: float = discount

    def change_state_to_legal_actions(
            self,
            new_state_to_legal_actions: tp.Dict[tp.Hashable, tp.Set[tp.Hashable]]
        ) -> None:
        states_diff_to_del = set(self._state_to_legal_actions) - set(new_state_to_legal_actions)
        states_diff_to_add = set(new_state_to_legal_actions) - set(self._state_to_legal_actions)
        for state in states_diff_to_del:
            del self._qvalues[state]
        for state in states_diff_to_add:
            for action in new_state_to_legal_actions:
                self.set_qvalue(state, action)
            
        states_intersection = set(new_state_to_legal_actions) & set(self._state_to_legal_actions)
        for state in states_intersection:
            actions_diff_to_del = self._state_to_legal_actions[state] - new_state_to_legal_actions[state]
            actions_diff_to_add = new_state_to_legal_actions[state] - self._state_to_legal_actions[state]
            for action in actions_diff_to_del:
                del self._qvalues[state][action]            
            for action in actions_diff_to_add:
                self.set_qvalue(state, action)
        self._state_to_legal_actions = new_state_to_legal_actions

    def get_qvalue(
            self,
            state: tp.Hashable,
            action: tp.Hashable
        ) -> tp.Optional[float]:
        """ Returns Q(state,action) """
        if state in self._qvalues:
            if action in self._qvalues[state]:
                return self._qvalues[state][action]
        return None

    def set_qvalue(
            self,
            state: tp.Hashable,
            action: tp.Hashable,
            value: tp.Optional[float] = None
        ) -> None:
        """ Sets the Qvalue for [state,action] to the given value """
        value = value if value is not None else self._init_qvalue
        if state not in self._qvalues:
            self._qvalues.update(
                {
                    state: {action: value}
                }
            )
        elif action not in self._qvalues[state]:
            self._qvalues[state].update(
                {action: self._init_qvalue}
            )
        else:
            self._qvalues[state][action] = value

    def get_value(self, state: tp.Union[str, int]) -> float:
        """
        Compute your agent's estimate of V(s) using current q-values
        V(s) = max_over_action Q(state,action) over possible actions.
        Note: please take into account that q-values can be negative.
        """
        possible_actions = self._state_to_legal_actions[state]

        # If there are no legal actions, return 0.0
        if len(possible_actions) == 0:
            return 0.0

        value = max([self.get_qvalue(state, action) for action in possible_actions])
        return value

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
        curr_qvalue = self.get_qvalue(state, action)
        new_qvalue = reward + self._discount * self.get_value(next_state)
        self.set_qvalue(
            state,
            action,
            curr_qvalue + self.alpha * (new_qvalue - curr_qvalue)
        )

    def get_best_action(self, state: tp.Hashable) -> tp.Hashable:
        """
        Compute the best action to take in a state (using current q-values).
        """
        possible_actions = list(self._state_to_legal_actions[state])
        # If there are no legal actions, return None
        if len(possible_actions) == 0:
            return None
        best_action = possible_actions[
            np.argmax([self.get_qvalue(state, action) for action in possible_actions])
        ]
        return best_action

    def get_action(self, state: tp.Hashable) -> tp.Hashable:
        """
        Compute the action to take in the current state, including exploration.
        With probability self.epsilon, we should take a random action.
            otherwise - the best policy action (self.get_best_action).

        Note: To pick randomly from a list, use random.choice(list).
              To pick True or False with a given probablity, generate uniform number in [0, 1]
              and compare it with your probability
        """
        possible_actions = list(self._state_to_legal_actions[state])

        # If there are no legal actions, return None.
        if len(possible_actions) == 0:
            return None

        unnormed_probs = np.array(
            [   
                self.get_qvalue(state, action) 
                    for action in possible_actions
            ]
        )
        unnormed_probs = np.exp(unnormed_probs / self._softmax_t)
        probs = unnormed_probs / sum(unnormed_probs)

        if self.epsilon > np.random.rand():
            chosen_action = np.random.choice(possible_actions)
        else:
            chosen_action = np.random.choice(possible_actions, p=probs)

        return chosen_action

