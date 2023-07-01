import typing as tp

import numpy as np


class BaseTableAgent:
    def __init__(
            self,
            state_to_legal_actions: tp.Dict[str, tp.Set[str]],
            epsilon: float,
            init_qvalue: float = 0.0,
            softmax_t: float = 1.0,
            waiting_strategy: tp.Tuple[
                tp.Union[float, tp.Tuple[float, float]], ...
            ] = (0.5,)
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
        self._state_to_legal_actions: \
            tp.Dict[str, tp.Set[str]] = state_to_legal_actions
        self._qvalues: tp.Dict[str, tp.Dict[str, float]] = {
            state: {
                action: self._init_qvalue 
                for action in state_to_legal_actions[state]
            } for state in state_to_legal_actions
        }
        self._epsilon: float = epsilon
        self._waiting_strategy: tp.Tuple[
            tp.Union[float, tp.Tuple[float, float]]
        ] = tuple(
            [
                tuple(elem) if isinstance(elem, list) else elem
                    for elem in waiting_strategy
            ]
        )

    def rewrite_states_and_actions(
            self,
            new_state_to_legal_actions: tp.Dict[str, tp.Set[str]]
    ) -> None:
        states_diff_to_del = set(self._state_to_legal_actions) - \
            set(new_state_to_legal_actions)
        states_diff_to_add = set(new_state_to_legal_actions) - \
            set(self._state_to_legal_actions)
        for state in states_diff_to_del:
            del self._qvalues[state]
        for state in states_diff_to_add:
            for action in new_state_to_legal_actions:
                self._set_qvalue(state, action)
            
        states_intersection = set(new_state_to_legal_actions) & \
            set(self._state_to_legal_actions)
        for state in states_intersection:
            actions_diff_to_del = self._state_to_legal_actions[state] - \
                new_state_to_legal_actions[state]
            actions_diff_to_add = new_state_to_legal_actions[state] - \
                self._state_to_legal_actions[state]
            for action in actions_diff_to_del:
                del self._qvalues[state][action]            
            for action in actions_diff_to_add:
                self._set_qvalue(state, action)
        self._state_to_legal_actions = new_state_to_legal_actions

    def _get_qvalue(
            self,
            state: str,
            action: str
    ) -> tp.Optional[float]:
        """ Returns Q(state,action) """
        if state in self._qvalues:
            if action in self._qvalues[state]:
                return self._qvalues[state][action]
        return None

    def _set_qvalue(
            self,
            state: str,
            action: str,
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
        value = max(
            [self._get_qvalue(state, action) for action in possible_actions]
        )
        return value

    def update(
            self, 
            state: str,
            action: str, 
            reward: tp.Union[int, float], 
            next_state: str
    ) -> None:
        raise NotImplementedError

    def get_action(self, state: str) -> tp.Tuple[str, float]:
        """
        Compute the action, which will be made in the current state
             (includes exploration).
        With probability self._epsilon, we should take a random action.
            otherwise - the best policy action (self.get_best_action).

        Note: To pick randomly from a list, use random.choice(list).
              To pick True or False with a given probablity, generate uniform
               number in [0, 1] and compare it with your probability.
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

        waiting_bounds = self._waiting_strategy[0]
        if isinstance(waiting_bounds, float):
            waiting_time = self._waiting_strategy[0]
        elif isinstance(waiting_bounds, tuple):
            waiting_time = np.random.randint(*waiting_bounds)
        else:
            raise RuntimeError(
                "Bad type of waiting_strategy element!"
            )
        self._waiting_strategy = (
            *self._waiting_strategy[1:], self._waiting_strategy[0]
        )
        return chosen_action, float(waiting_time)

