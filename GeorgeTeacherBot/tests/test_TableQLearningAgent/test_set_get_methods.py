import sys; sys.path.append("/home/david_tyuman/telegram/bots/GeorgeTeacherBot")
import typing as tp

import dataclasses
import pytest
import numpy as np

from TableQLearningAgent import QLearningAgent


@dataclasses.dataclass
class Case:
    state_to_legal_actions: tp.Dict[tp.Hashable, tp.Set[tp.Hashable]]
    alpha: float = 0.5
    epsilon: float = 0.25
    discount: float = 0.99
    reward: float = 0.0
    result: tp.Optional[float] = None
    name: tp.Optional[str] = None

    def __str__(self) -> str:
        if self.name is not None:
            return self.name
        return f"alpha={self.alpha}, epsilon={self.epsilon}, discount={self.discount}"


STATE_TO_LEGAL_ACTIONS_CASES = [
    Case({1: {""}}),
    Case({"s1": {1, 2, 3}, "s2": {2, 3}}, 0.05, 0.3, 0.9),
    Case({"s1": {"1"}, "s2": {"2"}, "s3": {"3"}}, 0.1, 0.5, 0.5),
    Case({("tuple", 1): {(1, 2, 3), 5}, ("2", (1, 2)): {"0", 0}, 0: (1, 2, 3)}, 0.01, 0.45, 0.8),
    Case({(): {(2), ()}, (): {"s", 0}, 0: {(1,), ()}, 1: {2, (8,)}}, 0.9, 0.2, 0.999)
]

@pytest.mark.parametrize('t', STATE_TO_LEGAL_ACTIONS_CASES, ids=str)
def test_get_qvalue(t: Case):
    legal_actions = t.state_to_legal_actions
    agent = QLearningAgent(
        alpha=t.alpha,
        epsilon=t.epsilon,
        discount=t.discount,
        state_to_legal_actions=t.state_to_legal_actions
    )
    for _ in range(30):
        state = np.random.choice(
            np.array(list(legal_actions.keys()), dtype=object)
        )
        action = np.random.choice(
            np.array(list(legal_actions[state]), dtype=object)
        )
        assert agent.get_qvalue(state, action) == 0.0


@pytest.mark.parametrize('t', STATE_TO_LEGAL_ACTIONS_CASES, ids=str)
def test_set_qvalue(t: Case):
    legal_actions = t.state_to_legal_actions
    agent = QLearningAgent(
        alpha=t.alpha,
        epsilon=t.epsilon,
        discount=t.discount,
        state_to_legal_actions=t.state_to_legal_actions
    )
    for _ in range(30):
        state = np.random.choice(
            np.array(list(legal_actions.keys()), dtype=object)
        )
        action = np.random.choice(
            np.array(list(legal_actions[state]), dtype=object)
        )
        value = np.random.randn() * 100
        agent.set_qvalue(state, action, value)
        assert agent.get_qvalue(state, action) == value

