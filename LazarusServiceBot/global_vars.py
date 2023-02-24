import logging
import os


def make_logger() -> logging.Logger:
    """
    :return: a logger into which data could be written.
    """
    logger = logging.getLogger('BaseLogger')
    logger.setLevel(logging.DEBUG)
    
    fh = logging.FileHandler('/home/david_tyuman/telegram_server/logs/LazarusServiceBot/debug.log')
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    
    logger.addHandler(fh)
   
    return logger


TOKEN = os.environ["LAZARUS_BOT_TOKEN"]
LOGGER = make_logger()

