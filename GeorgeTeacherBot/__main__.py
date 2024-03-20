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
        config["teacher_config"],
        config["path_to_the_log"],
    )

    while True:
        asked = bot.ask_word()
        message: str = bot.wait_for_a_message()  # TODO: create message class
        results: tp.List[str] = bot.process_the_message(asked, message)
        bot.send_result(results)
        bot.update_itself()
        bot.log_session()
        bot.wait()


if __name__ == "__main__":
    main()
