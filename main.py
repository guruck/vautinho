"""Modulo principal que executa o inventario de Telecom
"""
import os
import locale
import logging
from logging.handlers import TimedRotatingFileHandler  # , RotatingFileHandler

from datetime import date, datetime, timedelta

from models import VaultConfig, TicketConfig
from utils import read_configs, timeit, print_response, is_success
from hashicorp import VaultHashi


locale.setlocale(locale.LC_ALL, "Portuguese")
handlertime = TimedRotatingFileHandler("logs\\vault.log", when="d", interval=1, backupCount=5)
# handlersize = RotatingFileHandler("logs\\vault.log", maxBytes=2048, backupCount=5)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[handlertime])


@timeit
def main():
    """principal funcao"""
    today = date.today().strftime("%Y%m%d")
    # today = date(2023, 4, 10).strftime('%Y%m%d')
    configs = read_configs("./config.ini", "VaultConfig")
    configsTicket = read_configs("./config.ini", "ticket")
    str_path_src = os.getcwd()

    config = VaultConfig(**configs, today=today, str_path_src=str_path_src)
    ticket = TicketConfig(**configsTicket)

    now = datetime.now()
    metadata_info = ticket.model_dump()
    metadata_info["data_emissao"] = str(now.strftime("%Y/%m/%d"))
    metadata_info["data_vencimento"] = str((now + timedelta(hours=8760)).strftime("%Y/%m/%d"))
    certificado_nome = f"{metadata_info['sigla']}-{metadata_info['ambiente']}"

    vault = VaultHashi(config=config)
    token = vault.get_vault_token(username=configs["user"], password=configs["passwd"])
    print(token)

    current_crt = vault.read_current_certificate(current_cert_name=certificado_nome)
    print_response(current_crt)
    if is_success(current_crt.status_code):
        logging.info("certificado recuperado no auth")
        dict_current_crt = current_crt.json().get("data")
    else:
        dict_current_crt = {"token_bound_cidrs": ["10.0.0.10"], "token_policies": ["teste-policy"]}

    crt_resp = vault.gerar_certificado(crt_info=metadata_info)
    print_response(crt_resp)
    issue_crt = {
        "certificate": crt_resp.json()["data"]["certificate"],
        "issuing_ca": crt_resp.json()["data"]["issuing_ca"],
        "ca_chain": crt_resp.json()["data"]["ca_chain"],
        "private_key": crt_resp.json()["data"]["private_key"],
        "private_key_type": crt_resp.json()["data"]["private_key_type"],
        "serial_number": crt_resp.json()["data"]["serial_number"],
    }

    new_cert_auth = vault.cadatrar_novo_certificado_auth(
        inssue_crt=issue_crt, crt_info=metadata_info, current_crt=dict_current_crt
    )
    print_response(new_cert_auth)

    new_version_kv = vault.set_new_version_kv(inssue_crt=issue_crt, crt_info=metadata_info)
    print_response(new_version_kv)

    metadata_kv = vault.set_metadata_kv(metadata_info=metadata_info)
    print_response(metadata_kv)

    # payload = {"data": {"who": "Spring 18", "foott": "barz", "zipz": "zapz"}}
    # x = vault.set_secret_kv("secret", "hello-vault", payload)
    # x = vault.get_secret_kv("secret", "hello-vault")
    # print_response(x)

    # payload = {
    #     "max_versions": 15,
    #     "cas_required": "false",
    #     "delete_version_after": "3h25m19s",
    #     "custom_metadata": {"foo": "abc", "bar": "123", "baz": "5c07d823-3810-48f6-a147-4c06b5219e84"},
    # }
    # x = vault.set_secret_kv("secret", "hello-vault2", payload=payload, metadata=True)
    # print_response(x)
    # x = vault.get_secret_kv("secret", "hello-vault2", metadata=True)
    # print_response(x)


if __name__ == "__main__":
    main()
