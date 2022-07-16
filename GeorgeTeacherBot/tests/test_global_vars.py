import sys; sys.path.append("/home/david_tyuman/telegram/bots/GeorgeTeacherBot")
import dataclasses
import pytest
import string
import typing as tp
from itertools import chain

import numpy as np

from global_vars import change_layout


@dataclasses.dataclass
class Case:
    s1: str
    s2: str
    does_equal: bool
    name: tp.Optional[str] = None

    def __str__(self) -> str:
        if self.name is not None:
            return self.name
        return f"s1={self.s1}, s2={self.s2}, does_equal={self.does_equal}"


TEST_CASES = [
    Case(s1="", s2="", does_equal=True),
    Case(s1="a", s2="ф", does_equal=True),
    Case(s1="3", s2="3", does_equal=True),
    Case(s1="з", s2="p", does_equal=True),
    Case(s1="q2e", s2="й2у", does_equal=True),
    Case(s1="IйХхWwк", s2="Шq{[Ццr", does_equal=True),
    Case(s1="qdcpmQPDDMK", s2="йвсзьЙЗВВЬЛ", does_equal=True),
    Case(s1="q@#dcpmQP5DD;K", s2="й@#всзьЙЗ5ВВжЛ", does_equal=True),
    Case(s1="ХЙ#dcpP5D;K", s2="{Q#всзЗ5ВжЛ", does_equal=True),
    Case(s1="01923", s2="01923", does_equal=True),
    Case(s1="0Aaф1923", s2="0Ффa1923", does_equal=True),
    Case(s1="0Aaф19@#q", s2="0Ффa19@#й", does_equal=True),
    Case(s1="", s2="1", does_equal=False),
    Case(s1="a", s2="", does_equal=False),
    Case(s1="3", s2="33", does_equal=False),
    Case(s1="з", s2="з", does_equal=False),
    Case(s1="q2e", s2="йtwoу", does_equal=False),
    Case(s1="IйХхWwк", s2="Iq{[WWwr", does_equal=False),
    Case(s1="qdcpmQPDDMK", s2="qdcpmQPDDMK", does_equal=False),
    Case(s1="q@#dcpmQP5DD;K", s2="й@#всзьЙЗ5ВВжЛЛ", does_equal=False),
    Case(s1="ХЙ#dcpP5D;K", s2="{Q123зЗ5ВжK", does_equal=False)
]


@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_change_layout_1st_to_2nd(t: Case) -> None:
    assert (change_layout(t.s1) == t.s2) is t.does_equal

@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_change_layout_2nd_to_1st(t: Case) -> None:
    assert (t.s1 == change_layout(t.s2)) is t.does_equal

def test_change_layout_ring_property() -> None:
    symbols = list(
        chain(
            string.ascii_lowercase,
            string.ascii_uppercase, 
            string.digits, 
            string.punctuation
        )
    )

    for cnt in range(500):
        N = np.random.randint(0, 30)
        line = "".join([np.random.choice(symbols) for _ in range(N)])
        assert change_layout(change_layout(line)) == line

