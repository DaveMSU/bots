import sys; sys.path.append("/home/david_tyuman/telegram_server/bots")

from handler import WordsBaseHandler
from tools import parse_args, parse_config


def main():
    args = parse_args()
    config = parse_config(args.config)
    handler = WordsBaseHandler(config)
    handler.run()


if __name__ == "__main__":
    main()

