import time
import typing as tp

import numpy as np

from global_vars import DB_PASSWORD, TOKEN
from GeorgeBot import GeorgeBot
from tools import parse_args, parse_config

CHAT_ID = 746826672


def process(bot: GeorgeBot, process_config: tp.Dict[str, tp.Any]) -> None:
    bot.update_base()
    for _ in range(process_config["number_of_questions"]):
        bot.ask_word()
        bot.wait_for_an_message()
        bot.process_the_message()
        bot.send_result()
        bot.log_session()
        bot.wait(0.5)
    waiting_time = np.random.randint(*process_config["bounds"])
    bot.wait(waiting_time)


def main():
    args = parse_args()
    config = parse_config(args.config)
    bot = GeorgeBot(
        TOKEN,
        DB_PASSWORD,
        CHAT_ID,
        config["path_to_word_base"],
        config["data_pretrain_path"],
        **config["agent"],
    )
    bot.pretrain()

    while True:
        process(bot, config["process_params"])


if __name__ == "__main__":
    main()

