import typing as tp

from .agents import TableQLearningAgent


def create_agent_from_config(
        name: str,
        params: tp.Dict[str, float]
) -> tp.Any:
    return globals()[name](**params)

