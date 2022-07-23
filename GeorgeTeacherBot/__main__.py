import time
import typing as tp

import numpy as np

from global_vars import TOKEN, make_logger, parse_args, parse_config
from GeorgeBot import GeorgeBot

CHAT_ID = 746826672


def process(bot: GeorgeBot, process_config: tp.Dict[str, tp.Any]) -> None:
    bot.update_base()
    for _ in range(process_config["number_of_questions"]):
        bot.ask_word()
        bot.wait_for_an_message()
        bot.process_the_message()
        bot.send_result()
        bot.log_session()
        bot.wait(1.0)
    waiting_time = np.random.randint(*process_config["bounds"])
    bot.wait(waiting_time)


def main():
    args = parse_args()
    config = parse_config(args.config)
    bot = GeorgeBot(
        TOKEN,
        CHAT_ID,
        config["path_to_words_base"],        
        chat_logger=make_logger(
            config["chat_logger"]["name"],
            config["chat_logger"]["logging_file"],
            config["chat_logger"]["stdout"]
        ),
        ml_logger=make_logger(
            config["ml_logger"]["name"],
            config["ml_logger"]["logging_file"],
            config["ml_logger"]["stdout"]
        ),
        **config["agent"],
    )
    bot.pretrain(config["data_pretrain_path"])

    while True:
        process(bot, config["process_params"])


if __name__ == "__main__":
    main()

