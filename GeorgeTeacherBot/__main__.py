import shutil
import os
import time
import typing as tp

import numpy as np

from global_vars import TOKEN, make_logger, parse_args
from GeorgeBot import GeorgeBot

PATH_TO_WORDS_BASE = "./words_base.txt"
CHAT_ID = 746826672
NUMBER_OF_QUESTIONS = 2


def process(bot: GeorgeBot, with_delays: bool) -> None:
    bot.update_base(PATH_TO_WORDS_BASE)
    for _ in range(NUMBER_OF_QUESTIONS):
        bot.ask_word()
        bot.wait_for_an_message()
        bot.process_the_message()
        bot.send_result()
        bot.log_session()
        bot.wait(1.0)
    if with_delays:
        waiting_time = np.random.randint(10*60, 33*60)
    else: 
        waiting_time = 0
    bot.wait(waiting_time)


def do_backup() -> None:
    for log_name in ["chat", "learning"]:
        if not os.path.exists(f"./logs/{log_name}.log"):
            continue
        if os.path.exists(f"./logs/backups/{log_name}.log"):
            os.remove(f"./logs/backups/{log_name}.log")
        shutil.copy(f"./logs/{log_name}.log", f"./logs/backups/{log_name}.log")


def main():
    args = parse_args()
    bot = GeorgeBot(
        TOKEN, 
        CHAT_ID, 
        PATH_TO_WORDS_BASE,
        chat_logger=make_logger("ChatLogger", "./logs/chat.log"),
        ml_logger=make_logger("QLearningLogger", "./logs/learning.log"),
        alpha=0.1,
        epsilon=0.1,
        discount=0.5,
        init_qvalue=4.0,
        softmax_t=0.5
    )
    bot.pretrain("./logs/chat.log")

    while True:
        process(bot, args.with_delays)
        if args.do_backups:
            do_backup() 


if __name__ == "__main__":
    main()

