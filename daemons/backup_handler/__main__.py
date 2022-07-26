import sys; sys.path.append("/home/david_tyuman/telegram_server/bots")

from handler import BackupHandler
from tools import parse_args, parse_config


def main():
    args = parse_args()
    config = parse_config(args.config)
    handler = BackupHandler(config)
    handler.run()

if __name__ == "__main__":
    main()

