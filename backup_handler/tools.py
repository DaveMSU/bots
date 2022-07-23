import argparse
import json
import logging
import typing as tp


def parse_args() -> tp.Dict[str, tp.Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    return parser.parse_args()

def parse_config(config_path: str) -> tp.Dict[str, tp.Union[str, int]]:
    with open(config_path) as f:
        config = json.load(f)
    return config

def make_logger(
        logger_name: str,
        logging_file: str
    ) -> logging.Logger:
    """
    :return: a logger into which data could be written.
    """
    logger: logging.Logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(logging_file)
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)

    return logger

