import typing as tp

from .agents import *


def create_an_agent_from_a_config(
        name: str,
        params: tp.Dict[str, tp.Any]
) -> tp.Any:
    return globals()[name](**params)
