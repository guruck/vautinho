"""realiza a leitura das configuracoes do vault"""
import configparser
import os

from typing import Dict  # , List, Union


def read_configs(file: str, index: str) -> Dict[str, str]:  # Union[str, List[str]]]:
    if not os.path.exists(file):
        raise FileNotFoundError(f"{file} doesn't exist")

    config = configparser.ConfigParser(
        interpolation=None,
        converters={"list": lambda x: [i.strip() for i in x.split(",")]},
    )
    config.read(file, encoding="UTF-8")
    config = dict(config.items(index))

    return config
