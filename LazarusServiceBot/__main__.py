import sys; sys.path.append("/home/david_tyuman/telegram/bots")
import time
import typing as tp

from global_vars import TOKEN
from logging_tools import parse_and_log
from telegrambot import TelegramBot

TIME_TO_WAIT = 0.1  # Seconds.


def main():
    bot = TelegramBot(TOKEN)
    while True:
        time.sleep(TIME_TO_WAIT)
        message_data = bot.look_for_new_message()
        if message_data:
            parse_and_log(message_data)
            chat_id = message_data["message"]["chat"]["id"]
            message_text = message_data["message"]["text"]
            bot.send_message(chat_id, message_text)


if __name__ == "__main__":
    main()

