#TODO: fix all flake8 bugs
import json
import os
import pathlib
import pickle
import typing as tp

from ._utils import (
    LanguagePair,
    change_layout,
    levenstein_distance,
)
from .ml import Brain
from lib.types import Triplet


class ForeignLanguageTeacher:
    _SUPPORTED_LANGUAGES: tp.Set[tp.NamedTuple] = {
        LanguagePair(known="russian", target="english"),
    }

    def check_if_a_new_trained_brain_has_appeared_and_load_it(self) -> None:
        last_resource: pathlib.Path = self._brain_attributes["dir_with_brain_instances"] / max(
            filter(
                lambda abs_path: not abs_path.name.startswith("."),
                pathlib.Path(self._brain_attributes["dir_with_brain_instances"]).glob("*"),
            ),
            key=os.path.getctime,
        )
        retaining_timestamp: int = self._brain_attributes["meta"]["timestamp"]
        last_timestamp = int(last_resource.name)
        assert last_timestamp >= retaining_timestamp, "Timestamp bug!"
        if last_timestamp > retaining_timestamp:
            if last_timestamp > retaining_timestamp:
                with open(last_resource / "last.pckl", "rb") as fb:
                    self._brain_attributes["brain_itself"] = pickle.load(fb)
                with open(last_resource / "meta.json", "r") as f:
                    self._brain_attributes["meta"] = json.load(f)
                print(f"new brain has been loaded (ts: {last_timestamp})")  # TODO: rm this

    def __init__(
            self,
            known_language: str,
            target_language: str,
            path_to_the_brain_instances: str,
    ):
        self._languages: tp.NamedTuple = LanguagePair(
            known=known_language,
            target=target_language,
        )
        if self._languages not in ForeignLanguageTeacher._SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsuppored pair of languages appered ({pair_of_languages})"
                ", provide it with one of following pairs: "
                ", ".join([str(pair) for pair in SUPPORTED_LANGUAGES]) + "."
            )
        self._brain_attributes: tp.Dict[
                str,
                tp.Optional[tp.Union[pathlib.Path, Brain, dict]],
        ] = {
            "dir_with_brain_instances": pathlib.Path(path_to_the_brain_instances),
            "brain_itself": None,
            "meta": {
                "timestamp": -1,
            }
        }
        self.check_if_a_new_trained_brain_has_appeared_and_load_it()
       
    def ask(self) -> tp.Tuple[Triplet, float, tp.Dict[str, tp.Any]]:
        triplet: Triplet
        waiting_time: int
        debug_info: str
        triplet, waiting_time, debug_info = \
            self._brain_attributes["brain_itself"].generate()
        return triplet, waiting_time, debug_info

    @staticmethod
    def _check_the_similarity_of_the_lines(
            line: str,
            weak_line,
            degree: int
    ) -> bool:
        line, weak_line = line.lower(), weak_line.lower()
        lev_dist: int = min(
            levenstein_distance(line, weak_line),
            levenstein_distance(line, change_layout(weak_line))
        )
        return lev_dist <= degree

    def process_a_question_and_an_answer(
            self,
            question: Triplet,
            answer: str,
    ) -> bool:
        if question.language_to_answer == self._languages.target:
            sim_degree = 0
        elif question.language_to_answer == self._languages.known:
            sim_degree = 1

        is_the_answer_right: bool = self._check_the_similarity_of_the_lines(
            line=question.phrase_to_answer,
            weak_line=answer,
            degree=sim_degree,
        )
        return is_the_answer_right
