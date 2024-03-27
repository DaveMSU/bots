import pymysql
import typing as tp
from textwrap import dedent

from ._utils import create_an_agent_from_a_config
from .agents import BaseTableAgent
from global_vars import DB_PASSWORD
from lib.types import Triplet


class Brain:
    def __init__(
            self,
            path_to_the_base: str,
            path_to_the_log: str,
            agent_config: tp.Dict[str, tp.Any],
    ):
        self._sole_state: str = "sole_state"
        self._path_to_the_log: str = path_to_the_log
        self._base: tp.Dict[str, Triplet] = dict()
        self._familiarize_with_all_possible_pair_phrases(path_to_the_base)

        agent_config["params"].update(  # TODO: make next line shorter
            {"state_to_legal_actions": {self._sole_state: set(self._base.values())}}
        )
        self._prefrontal_cortex: BaseTableAgent = create_an_agent_from_a_config(
            **agent_config
        )
        self._pretrain()

    def generate(self) -> tp.Tuple[Triplet, float, tp.Dict[str, tp.Any]]:
        """
        The only one unprivate method.
        """
        return self._prefrontal_cortex.get_action(self._sole_state)

    def _familiarize_with_all_possible_pair_phrases(
            self,
            path_to_the_base: str,
    ) -> None:
        database_name, table_name = path_to_the_base.split(".")
        connection = pymysql.connect(  # TODO: remove hard code.
            host='localhost',
            user='root',
            password=DB_PASSWORD,
            db=database_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with connection.cursor() as cursor:
                query = dedent(
                    f"""
                    SELECT * FROM {table_name};
                    """
                )
                cursor.execute(query)
                languages: tp.Tuple[str, str] = ("english", "russian")
                for row in cursor:
                    for i in [0, 1]:
                        triplet = Triplet(
                            phrase_to_ask=row[languages[i]],
                            language_to_ask=languages[i],
                            phrase_to_answer=row[languages[i ^ 1]],
                            language_to_answer=languages[i ^ 1],
                            context=row["context"]  # TODO: fix the duplication
                        )
                        # TODO: optimize memory usage
                        self._base.update({row[languages[i]]: triplet})
        finally:
            connection.close()

    def _create_a_sequence_portion(
            self,
            row: tp.Dict[str, tp.Any]
    ) -> tp.Dict[str, tp.Any]:
        return {
            "state": self._sole_state,
            "action": (
                self._base[row["phrase_to_ask"]],
                row["timestamp"]
            ),
            "reward": float(not bool(row["is_the_answer_right"])),
            "next_state": self._sole_state,
        }

    def _pretrain(self) -> None:
        print("pretrain in")  # TODO: rm this line
        database_name, table_name = self._path_to_the_log.split(".")
        connection = pymysql.connect(  # TODO: remove hard code.
            host='localhost',
            user='root',
            password=DB_PASSWORD,
            db=database_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with connection.cursor() as cursor:
                query = dedent(
                    f"""
                    SELECT * FROM {table_name};
                    """
                )
                cursor.execute(query)
                whole_sequence: tp.List[tp.Any] = [
                    self._create_a_sequence_portion(row) for row in cursor
                ]
                assert len(whole_sequence)
                self._last_timestamp: int = whole_sequence[-1]["action"][1]
                print("pretrain update in")  # TODO: rm this line
                self._prefrontal_cortex.update(whole_sequence)
                print("pretrain update out")  # TODO: rm this line
        finally:
            connection.close()
        print("pretrain out")  # TODO: rm this line

    def finetune(self, path_to_the_table: tp.Optional[str] = None) -> None:
        print("finetune in")  # TODO: rm this line
        if path_to_the_table is None:
            path_to_the_table = self._path_to_the_log
        database_name, table_name = path_to_the_table.split(".")
        
        connection = pymysql.connect(  # TODO: remove hard code.
            host='localhost',
            user='root',
            password=DB_PASSWORD,
            db=database_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with connection.cursor() as cursor:
                query = dedent(
                    f"""
                    SELECT *
                    FROM {table_name}
                    WHERE timestamp > {self._last_timestamp};
                    """
                )
                # TODO: to add schema checking
                cursor.execute(query)
                whole_sequence: tp.List[tp.Any] = [
                    self._create_a_sequence_portion(row) for row in cursor
                ]
                print("finetune update in")  # TODO: rm this line
                self._prefrontal_cortex.update(whole_sequence)
                print("finetune update out")  # TODO: rm this line
            if len(whole_sequence):
                self._last_timestamp: int = whole_sequence[-1]["action"][1]
        finally:
            connection.close()
        print("finetune out")  # TODO: rm this line
