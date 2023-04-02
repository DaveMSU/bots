import typing as tp

import numpy as np


class BaseTableAgent:
    def __init__(
            self,
            state_to_legal_actions: tp.Dict[tp.Hashable, tp.Set[tp.Hashable]],
            epsilon: float,
            init_qvalue: float = 0.0,
            softmax_t: float = 1.0
    ):
        """
        Q-Learning Agent
        based on https://inst.eecs.berkeley.edu/~cs188/sp19/projects.html
        Instance variables you have access to
          - self._epsilon (exploration prob)

        Functions you should use
          - self.get_action(state)
          - self.update(...)
          - self.rewrite_states_and_actions(new_state_to_legal_actions)
        """
        self._softmax_t = softmax_t
        self._init_qvalue = init_qvalue
        self._state_to_legal_actions: tp.Dict[tp.Hashable, tp.Set[tp.Hashable]] = \
            state_to_legal_actions
        self._qvalues: tp.Dict[tp.Hashable, tp.Dict[tp.Hashable, float]] = {
            state: {
                action: self._init_qvalue for action in state_to_legal_actions[state]
            } for state in state_to_legal_actions
        }
        self._epsilon: float = epsilon

    def rewrite_states_and_actions(
            self,
            new_state_to_legal_actions: tp.Dict[tp.Hashable, tp.Set[tp.Hashable]]
    ) -> None:
        states_diff_to_del = set(self._state_to_legal_actions) - set(new_state_to_legal_actions)
        states_diff_to_add = set(new_state_to_legal_actions) - set(self._state_to_legal_actions)
        for state in states_diff_to_del:
            del self._qvalues[state]
        for state in states_diff_to_add:
            for action in new_state_to_legal_actions:
                self._set_qvalue(state, action)
            
        states_intersection = set(new_state_to_legal_actions) & set(self._state_to_legal_actions)
        for state in states_intersection:
            actions_diff_to_del = self._state_to_legal_actions[state] - new_state_to_legal_actions[state]
            actions_diff_to_add = new_state_to_legal_actions[state] - self._state_to_legal_actions[state]
            for action in actions_diff_to_del:
                del self._qvalues[state][action]            
            for action in actions_diff_to_add:
                self._set_qvalue(state, action)
        self._state_to_legal_actions = new_state_to_legal_actions

    def _get_qvalue(
            self,
            state: tp.Hashable,
            action: tp.Hashable
    ) -> tp.Optional[float]:
        """ Returns Q(state,action) """
        if state in self._qvalues:
            if action in self._qvalues[state]:
                return self._qvalues[state][action]
        return None

    def _set_qvalue(
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
            assert np.isclose(value, self._init_qvalue)
        #     self._qvalues[state].update({action: value})
            self._qvalues[state][action] = value
        else:
            self._qvalues[state][action] = value

    def _get_value(self, state: tp.Union[str, int]) -> float:
        """
        Compute your agent's estimate of V(s) using current q-values
        V(s) = max_over_action Q(state,action) over possible actions.
        Note: please take into account that q-values can be negative.
        """
        possible_actions = self._state_to_legal_actions[state]
        if len(possible_actions) == 0:
            return 0.0
        value = max([self._get_qvalue(state, action) for action in possible_actions])
        return value

    def update(
            self, 
            state: tp.Hashable, 
            action: tp.Hashable, 
            reward: tp.Union[int, float], 
            next_state: tp.Hashable
    ) -> None:
        raise NotImplementedError

#     def get_best_action(self, state: tp.Hashable) -> tp.Hashable:
#         """
#         Compute the best action to take in a state (using current q-values).
#         """
#         possible_actions = list(self._state_to_legal_actions[state])
#         # If there are no legal actions, return None
#         if len(possible_actions) == 0:
#             return None
#         best_action = possible_actions[
#             np.argmax([self._get_qvalue(state, action) for action in possible_actions])
#         ]
#         return best_action

    def get_action(self, state: tp.Hashable) -> tp.Hashable:
        """
        Compute the action to take in the current state, including exploration.
        With probability self._epsilon, we should take a random action.
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
                self._get_qvalue(state, action) 
                    for action in possible_actions
            ]
        )
        unnormed_probs = np.exp(unnormed_probs / self._softmax_t)
        probs = unnormed_probs / sum(unnormed_probs)

        if self._epsilon > np.random.rand():
            chosen_action = np.random.choice(possible_actions)
        else:
            chosen_action = np.random.choice(possible_actions, p=probs)

        return chosen_action

