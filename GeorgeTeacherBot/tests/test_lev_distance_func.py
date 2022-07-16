import sys; sys.path.append("/home/david_tyuman/telegram/bots/GeorgeTeacherBot")
import dataclasses
import os
import pytest
import psutil
import time
import typing as tp

from GeorgeBot import GeorgeBot


@dataclasses.dataclass
class Case:
    s1: str
    s2: str
    distance: int
    name: tp.Optional[str] = None

    def __str__(self) -> str:
        if self.name is not None:
            return self.name
        return f"s1={self.s1}, s2={self.s2}, lev_dst={self.distance}"


TEST_CASES = [
    Case(s1="", s2="", distance=0),
    Case(s1="", s2="a", distance=1),
    Case(s1="b", s2="", distance=1),
    Case(s1="", s2="abcde", distance=5),
    Case(s1="edc", s2="", distance=3),
    Case(s1="a", s2="a", distance=0),
    Case(s1="a", s2="ab", distance=1),
    Case(s1="ed", s2="ea", distance=1),
    Case(s1="Qd", s2="d", distance=1),
    Case(s1="Hello", s2="Hi", distance=4),
    Case(s1="Hello", s2="hi", distance=5),
    Case(s1="Ho", s2="Hello", distance=3),
    Case(s1="QwErt123!?", s2="QwErt123!?", distance=0),
    Case(s1="QwErt123!?", s2="QwERt12!?", distance=2),
    Case(s1="wErt!@3!?", s2="QwErt123!?", distance=3),
    Case(
        s1="Hello, my, friend! How are you filling yourself? It is very good?",
        s2="hello, my friend! how are you fjlling yourself? It iss wery good?",
        distance=6,
        name="middle_size_test"
    ),
    Case(
        s1="Hello, my, friend! How are you filling yourself? It is very good?",
        s2="Hello, my, friend! How are you filling yourself? It is very good?",
        distance=0,
        name="middle_size_test.two_same_lines"
    ),
    Case(
        s1="Hello, my, friend! How are you filling yourself? It is very good?",
        s2="AZSXdcfv156v82cbc29ec29ecneucnencecew992cm29d29deicm2d9jcn2e9cn2e",
        distance=65,
        name="middle_size_test.two_fully_different_lines"
    ),
    Case(s1="A"*100, s2="A"*100, distance=0, name="big_test.100.two_same_lines"),
    Case(s1="A"*100, s2="B"*100, distance=100, name="big_test.100.two_fully_different_lines"),
    Case(s1="A"*1000, s2="A"*1000, distance=0, name="big_test.1000.two_same_lines"),
    Case(s1="A"*1000, s2="B"*1000, distance=1000, name="big_test.1000.two_fully_different_lines")
]


@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_function_return_correct_value(t: Case) -> None:
    assert GeorgeBot._lev_dist(t.s1, t.s2) == t.distance, "Incorrect result!"


@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_function_speed(t: Case) -> None:
    start_time = time.monotonic()
    GeorgeBot._lev_dist(t.s1, t.s2)
    end_time = time.monotonic()
    assert end_time - start_time < 1.5, "Working time is too long!"


@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_function_memory_usage(t: Case) -> None:
    pid = os.getpid()
    python_process = psutil.Process(pid)
    memory_use_before_func_call = python_process.memory_info()[0] / (2. ** 10)  # memory use in KiB.
    GeorgeBot._lev_dist(t.s1, t.s2)
    memory_use_after_func_call = python_process.memory_info()[0] / (2. ** 10)
    assert memory_use_after_func_call - memory_use_before_func_call < 1.0, "Too much memory usage!"

