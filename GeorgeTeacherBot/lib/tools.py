import typing as tp

from .agents import *


def create_agent_from_config(
        name: str,
        params: tp.Dict[str, float]
) -> tp.Any:
    return globals()[name](**params)
