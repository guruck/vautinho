"""Modulo principal que executa o inventario de Telecom
"""
import locale
import logging
from logging.handlers import TimedRotatingFileHandler  # , RotatingFileHandler

from datetime import date
from models import VaultConfig
from utils import read_vault_config, timeit, print_response
from hashicorp import Vault


locale.setlocale(locale.LC_ALL, "Portuguese")
handlertime = TimedRotatingFileHandler("logs\\vault.log", when="d", interval=1, backupCount=5)
# handlersize = RotatingFileHandler("logs\\vault.log", maxBytes=2048, backupCount=5)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[handlertime])


@timeit
def main():
    """principal funcao"""
    today = date.today().strftime("%Y%m%d")
    # today = date(2023, 4, 10).strftime('%Y%m%d')
    configs = read_vault_config("./config.ini", "VaultConfig")

    config = VaultConfig(**configs, today=today)
    logging.info(config)

    vault = Vault(config=config)
    client = vault.get_vault_client()

    # x = vault.get_policy("admin")
    # print_response(x)

    # payload = {"data": {"who": "Spring 18", "foott": "barz", "zipz": "zapz"}}
    # x = vault.set_secret_kv("secret", "hello-vault", payload)
    x = vault.get_secret_kv("secret", "hello-vault")
    print_response(x)

    payload = {
        "max_versions": 15,
        "cas_required": "false",
        "delete_version_after": "3h25m19s",
        "custom_metadata": {"foo": "abc", "bar": "123", "baz": "5c07d823-3810-48f6-a147-4c06b5219e84"},
    }
    x = vault.set_secret_kv("secret", "hello-vault2", payload=payload, metadata=True)
    print_response(x)
    x = vault.get_secret_kv("secret", "hello-vault2", metadata=True)
    print_response(x)

    client.logout()


if __name__ == "__main__":
    main()
