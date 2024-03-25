import json
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

    def _create_brain_dict(self, path: str) -> tp.Dict[
            str,
            tp.Union[
                pathlib.Path,
                Brain,
                tp.Dict[str, tp.Any]
            ],
    ]:
        path_to_the_last_brain_dir = pathlib.Path(path)
        with open(path_to_the_last_brain_dir / "last.pckl", "rb") as fb:
            brain: Brain = pickle.load(fb)
        with open(path_to_the_last_brain_dir / "meta.json", "r") as f:
            additional_brain_information: tp.Dict[str, tp.Any] = json.load(f)
        return {
            "last_one_dir": path_to_the_last_brain_dir,
            "brain_itself": brain,
            "meta": additional_brain_information,
        }

    def __init__(
            self,
            known_language: str,
            target_language: str,
            last_brain_path: str,
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
        self._brain_info: tp.Dict[
                str,
                tp.Union[pathlib.Path, Brain, dict],
        ] = self._create_brain_dict(path=last_brain_path)
       
    def ask(self) -> tp.Tuple[Triplet, float, tp.Dict[str, tp.Any]]:
        triplet: Triplet
        waiting_time: int
        debug_info: str
        triplet, waiting_time, debug_info = \
            self._brain_info["brain_itself"].generate()
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

    def process_a_question_and_the_answer(
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

    def check_if_a_new_trained_brain_has_appeared_and_load_it(self) -> None:
        with open(self._brain_info["last_one_dir"] / "meta.json", "r") as f:
            meta_of_the_last_brain: tp.Dict[str, tp.Any] = json.load(f)
            last_timestamp: int = meta_of_the_last_brain["timestamp"]
            cur_timestamp: int = self._brain_info["meta"]["timestamp"]
            assert last_timestamp >= cur_timestamp, "Timestamp bug!"
            if last_timestamp > cur_timestamp:
                with open(self._brain_info["last_one_dir"] / "last.pckl", "rb") as fb:
                    self._brain_info["brain_itself"] = pickle.load(fb)
                self._brain_info["meta"] = meta_of_the_last_brain
