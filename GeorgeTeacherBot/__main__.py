from global_vars import DB_PASSWORD, TOKEN
from george_bot import GeorgeBot
from tools import parse_args, parse_config


CHAT_ID = 746826672


def main():
    args = parse_args()
    config: tp.Dict[str, tp.Any] = parse_config(args.config)
    bot = GeorgeBot(
        TOKEN,
        DB_PASSWORD,
        CHAT_ID,
        config["teachers_config"],
        config["path_to_the_log"],
    )

    while True:
        bot.conduct_one_session_with_a_student()


if __name__ == "__main__":
    main()
