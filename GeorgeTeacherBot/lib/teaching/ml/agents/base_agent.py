import sys; sys.path.append("/home/david_tyuman/telegram_server/bots/GeorgeTeacherBot")  # TODO: remove

import typing as tp

import numpy as np

from lib.types import Triplet


class BaseTableAgent:
    def __init__(
            self,
            state_to_legal_actions: tp.Dict[str, tp.Set[Triplet]],
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
        self._state_to_legal_actions = state_to_legal_actions
        self._qvalues: tp.Dict[str, tp.Dict[Triplet, float]] = {
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
            new_state_to_legal_actions: tp.Dict[str, tp.Set[Triplet]]
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
            action: Triplet
    ) -> tp.Optional[float]:
        """ Returns Q(state,action) """
        if state in self._qvalues:
            if action in self._qvalues[state]:
                return self._qvalues[state][action]
        return None

    def _set_qvalue(
            self,
            state: str,
            action: Triplet,
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
        assert len(sequence) >= 1  # at least one
        for seq_portion in sequence:
            assert "state" in seq_portion  # type: str
            assert "action" in seq_portion  # type: tp.Tuple[Triplet, int]
            assert "reward" in seq_portion  # type: tp.Union[int, float]
            assert "next_state" in seq_portion  # type: str
            assert len(seq_portion.keys()) == 4  # only these 4 variable
        raise NotImplementedError

    def _get_how_long_to_wait(self) -> float:
        raise NotImplementedError

    def get_action(
            self, state: str
    ) -> tp.Tuple[
        Triplet,
        float,
        tp.Dict[str, tp.Union[bool, int, float, str]]
    ]:
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

        q_values = np.array(
            [
                self._get_qvalue(state, action)
                for action in possible_actions
            ]
        )
        unnormed_probs = np.exp(q_values / self._softmax_t)
        probs = unnormed_probs / sum(unnormed_probs)

        epsilon_flag: bool = self._epsilon > np.random.rand()
        if epsilon_flag:
            chosen_action_index = np.random.choice(
                range(len(possible_actions))
            )
        else:
            chosen_action_index = np.random.choice(
                range(len(possible_actions)),
                p=probs
            )
        chosen_action = possible_actions[chosen_action_index]
        waiting_time = self._get_how_long_to_wait()
        debug_info = {
            "epsilon": epsilon_flag,
            "q_value": str(q_values[chosen_action_index])
        }
        return chosen_action, waiting_time, debug_info
