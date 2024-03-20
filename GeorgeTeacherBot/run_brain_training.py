import sys; sys.path.append("/home/david_tyuman/telegram_server/bots")  # TODO: remove that kinda import.

import datetime
import json
import pathlib
import pickle
import shutil
import time

from lib.teaching.ml import Brain
from tools import parse_args, parse_config


WAITING_TIME_BEFORE_ANOTHER_FINETUNE_ATTEMPT_IN_SECONDS: float = 10.0


def do_backup_of_the_last_resources_and_create_new_ones(
        dir_path: pathlib.Path
) -> None:
    with open(dir_path / "meta.json", "r") as f:
        timestamp = str(json.load(f)["timestamp"])
    backup_dir_path: pathlib.Path = dir_path / timestamp
    backup_dir_path.mkdir(parents=False, exist_ok=False)
    for file_name in ["meta.json", "last.pckl"]:
        shutil.move(
            src=dir_path / file_name,
            dst=backup_dir_path / file_name,
        )


def main():
    args = parse_args()
    config = parse_config(args.config)
    path_to_the_last_brain_dir = pathlib.Path(
        config["path_to_the_last_brain_dir"]
    )
    
    brain_instance: Brain = Brain(
        path_to_the_base=config["path_to_the_base"],
        path_to_the_log=config["path_to_the_log"],
        agent_config=config["agent"],
    )
    while True:
        print(time.time())
        brain_instance.finetune()
        do_backup_of_the_last_resources_and_create_new_ones(
            dir_path=path_to_the_last_brain_dir
        )
        with open(path_to_the_last_brain_dir / "last.pckl", "wb") as f:
            pickle.dump(brain_instance, f)
        with open(path_to_the_last_brain_dir / "meta.json", "w") as f:
            meta: tp.Dict[str, int] = {
                "timestamp": round(datetime.datetime.utcnow().timestamp()),
            }
            json.dump(meta, f)
        # TODO: rewrite this to react by a signal, notconst a time span.
        time.sleep(WAITING_TIME_BEFORE_ANOTHER_FINETUNE_ATTEMPT_IN_SECONDS)
        
        
if __name__ == "__main__":
    main()
