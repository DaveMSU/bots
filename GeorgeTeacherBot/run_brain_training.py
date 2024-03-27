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


def main():
    args = parse_args()
    config = parse_config(args.config)
    path_to_the_instances = pathlib.Path(
        config["path_to_the_instances"]
    )
    
    brain_instance: Brain = Brain(
        path_to_the_base=config["path_to_the_base"],
        path_to_the_log=config["path_to_the_log"],
        agent_config=config["agent"],
    )
    while True:
        brain_instance.finetune()
        print("Finetune has finished!")  # TODO: rm this line.

        cur_timestamp: int = round(datetime.datetime.utcnow().timestamp())
        resource_name = str(cur_timestamp)
        raw_abs_path = path_to_the_instances / f".{resource_name}"
        abs_path = path_to_the_instances / f"{resource_name}"

        raw_abs_path.mkdir(parents=False, exist_ok=False)
        with open(raw_abs_path / "last.pckl", "wb") as f:
            pickle.dump(brain_instance, f)
        with open(raw_abs_path / "meta.json", "w") as f:
            meta: tp.Dict[str, int] = {
                "timestamp": cur_timestamp,
            }
            json.dump(meta, f)
        shutil.move(src=raw_abs_path, dst=abs_path)

        # TODO: rewrite this to react by a signal, notconst a time span.
        time.sleep(WAITING_TIME_BEFORE_ANOTHER_FINETUNE_ATTEMPT_IN_SECONDS)
        
        
if __name__ == "__main__":
    main()
