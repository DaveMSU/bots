import sys; sys.path.append("/home/david_tyuman/telegram_server/bots")  # TODO: remove that kinda import.

import datetime
import logging
import os
import pathlib
import time # TODO: Remove this line.
import typing as tp
from textwrap import dedent

import pymysql

from tools import make_logger


DB_PASSWORD =  os.environ["MYSQL_ROOT_PASSWORD"]


class WordsBaseHandler:
    def __init__(self, config: tp.Dict[str, tp.Union[str, int]]):
        self._queue_path = pathlib.Path(config["path_to_queue"])
        self._base_path = config["path_to_base"]
        self._portion_size: int = config["portion_size"]
        self._logger: logging.Logger = make_logger(
            logger_name="WordsBaseHandler",
            logging_file=config["logging_params"]["logging_file"],
            stdout=config["logging_params"]["stdout"]
        )
        dt = datetime.datetime.strptime(config["hike_in_time"], "%H:%M:%S")
        self._next_hike_time = datetime.datetime.now()
        self._next_hike_time += datetime.timedelta(days=1)
        self._next_hike_time = self._next_hike_time.replace(
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second
        )
        self._logger.debug("Handler created!")
        self._logger.debug(f"Next hike time - {self._next_hike_time}.")

    def _is_it_time_to_go_in_queue(self) -> bool:
        return datetime.datetime.now() >= self._next_hike_time

    def _check_paths_existence(self):
        if not self._queue_path.exists():
            self._logger.warn(f"File '{self._queue_path}' do not exists!")
        return self._queue_path.exists()

    def _transport_words_from_queue_to_base(self):
        database_name, table_name = self._base_path.split('.')
        if not self._check_paths_existence():
            raise FileNotFoundError(
                "Some files unexists, so transportation words"
                " form words queue to words base failed!"
            ) 
        with open(self._queue_path, "r") as source:
            all_queue_lines = source.readlines()
        if len(all_queue_lines) < self._portion_size:
            raise ValueError(
                "Variable 'self._portion_size' equal"
                f" to {self._portion_size}, but file"
                f" '{self._queue_path}' consists only"
                f" from {len(all_queue_lines)} lines."
            )
        parsed_portion_queue_lines = [  # TODO: rewrite it by clear way.
            {
                "english": "'" + line.split("  # ")[0].split(" - ")[0] + "'",
                "russian": "'" + line.split("  # ")[0].split(" - ")[-1] + "'",
                "context": "'" + repr(line.split("  # ")[-1].strip().replace("'", "''")).strip("'") + "'"
            }
                for line in all_queue_lines[:self._portion_size]
        ]
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password=DB_PASSWORD,
            db=database_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with connection.cursor() as cursor:
                for dicted_line in parsed_portion_queue_lines:
                    columns, values = zip(*dicted_line.items())

                    query = dedent(
                        f"""
                        INSERT {table_name}(
                            {", ".join(columns)}
                        ) VALUES (
                            {", ".join(map(str, values))}
                        );       
                        """
                    )
                    cursor.execute(query)
            connection.commit()
        finally:
            connection.close()

        with open(self._queue_path, "w") as dist: 
            dist.writelines(all_queue_lines[self._portion_size:])
        self._logger.debug(
            f"From '{self._queue_path}' file was"
            f" transport first {self._portion_size}"
            f" lines to '{self._base_path}' file."
        )
        
    def _inc_next_hike_time(self):
        self._next_hike_time += datetime.timedelta(days=1)
        self._logger.debug(
            "Private variable 'next_hike_time'"
            " have been incremented. For now it"
            f" is {self._next_hike_time}."
        )
        
    def run(self):
        try:
            while True:
                if self._is_it_time_to_go_in_queue():
                    self._transport_words_from_queue_to_base()
                    self._inc_next_hike_time()
                time.sleep(1.0)

        except KeyboardInterrupt:
            pass

        except BaseException as err:
            self._logger.error(
                "Exit from while loop in run method"
                " without using KeyboardInterrupt. "
                f"Next exception occured: {str(err)}."
            )

