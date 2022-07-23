import datetime
import shutil
import os
import pathlib
import time
import typing as tp
from itertools import chain

from tools import make_logger


class BackupHandler:
    def __init__(self, config):
        self._period: int = config["backup_period"]
        self._matching: tp.List[tp.Dict[str, str]] = config["matching"]
        self._logger = make_logger(
            logger_name="BackupHandler", 
            logging_file=config["logging_params"]["logging_file"],
            stdout=config["logging_params"]["stdout"]
        )

    def _add_date_as_postfix(self, path: pathlib.Path) -> pathlib.Path:
        date = datetime.datetime.now()
        postfix = str(date).replace(" ", "T").split(".")[0]
        return path.parent / (path.stem + "_" + postfix + path.suffix)

    def _do_backup(self) -> None:
        for data_fold in self._matching:
            original_path = pathlib.Path(data_fold["original"])
            copied_path_pattern = pathlib.Path(data_fold["copy"])
            if not original_path.exists():
                self._logger.warn(f"File '{original_path}' do not exists!")
                continue
            for parent_path in reversed(copied_path_pattern.parents):
                if not parent_path.exists():
                    parent_path.mkdir()
                    self._logger.warn(
                        f"{parent_path} dir do"
                        " not exists, so it was creared."
                    )
            copied_path = self._add_date_as_postfix(copied_path_pattern)
            shutil.copy(original_path, copied_path)
            self._logger.debug(
                f"File '{original_path}' copied to '{copied_path}' path."
            )

    def run(self) -> None:
        try:
            while True:
                self._do_backup()
                time.sleep(self._period)

        except KeyboardInterrupt:
            pass

        except BaseException as err:
            self._logger.warn(
                "Exit from while loop in run method"
                " without using KeyboardInterrupt. "
                f"Next exception occured: {str(err)}."
            )

