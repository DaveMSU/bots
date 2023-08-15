import time
import typing as tp

import numpy as np

from global_vars import DB_PASSWORD, TOKEN
from george_bot import GeorgeBot
from tools import parse_args, parse_config


CHAT_ID = 746826672


def main():
    args = parse_args()
    config = parse_config(args.config)
    bot = GeorgeBot(
        TOKEN,
        DB_PASSWORD,
        CHAT_ID,
        config["path_to_word_base"],
        config["data_pretrain_path"],
        config["agent"],
    )
    bot.pretrain()

    while True:
        bot.ask_word()
        bot.wait_for_an_message()
        bot.process_the_message()
        bot.send_result()
        bot.update()
        bot.log_session()
        bot.wait()


if __name__ == "__main__":
    main()

