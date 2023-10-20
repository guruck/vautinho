"""Classe operacional Vault Hashicorp"""
import hvac
import requests
import logging
import json

from requests.models import Response
from hvac import Client

from models import VaultConfig


class VaultHashi:
    def __init__(self, config: VaultConfig):
        self._conf = config
        self.hashicorp_uri = f"{config.uri}:{config.port}"
        self.hashicorp_ca_cert = f"{config.str_path_src}\\{config.pki_ca_cert}"
        self.hashicorp_int_cert = f"{config.str_path_src}\\{config.pki_int_cert}"
        self.hashicorp_key = f"{config.str_path_src}\\{config.pki_key}"
        self._token = ""

    def get_vault_token(self, username: str, password: str) -> str:
        """faz login e retorna token para uso"""
        logging.debug("Vault.get_vault_token")
        logging.info("realizando login no cofre Vault atraves do LDAP")
        try:
            client = Client(url=self.hashicorp_uri, verify=self.hashicorp_ca_cert)
            # cli = client.auth.ldap.login(username=username, password=password)
            cli = client.auth.userpass.login(username=username, password=password)
            if client.is_authenticated():
                logging.info("login efetuado com sucesso")
                self._token = cli["auth"]["client_token"]

            return self._token
        except Exception as e:
            logging.error("falha na autenticacao %s", e)
            raise NotImplementedError("visualizar LOG") from e

    def get_vault_client(self):
        """
        Instantiates a hvac / vault client.
        :param vault_url: string, protocol + address + port for the vault service
        :param certs: tuple, Optional tuple of self-signed certs to use for verification
                with hvac's requests adapater.
        :return: hvac.Client
        """
        logging.info("Retrieving a vault (hvac) client...")

        # vault_client = hvac.Client(url=self._url, cert=certs)
        vault_client = Client(url=self.hashicorp_uri)
        login_response = vault_client.auth.userpass.login(self._conf.user, self._conf.passwd)
        if not vault_client.is_authenticated():
            error_msg = "Unable to authenticate to the Vault service"
            raise hvac.exceptions.Unauthorized(error_msg)

        self._token = login_response["auth"]["client_token"]
        logging.debug(self._token)

        return vault_client

    def get_vault_client_by_certify(self):
        """
        Instantiates a hvac / vault client.
        :param vault_url: string, protocol + address + port for the vault service
        :param certs: tuple, Optional tuple of self-signed certs to use for verification
                with hvac's requests adapater.
        :return: hvac.Client
        """
        logging.info("Retrieving a vault (hvac) client...")
        certs = (self.hashicorp_int_cert, self.hashicorp_key)
        try:
            vault_client = Client(url=self.hashicorp_uri, cert=certs, verify=self.hashicorp_ca_cert, timeout=5.0)
            vault_client.auth.cert.login()
            if vault_client.is_authenticated():
                logging.info("autenticado com sucesso")
                return vault_client
        except Exception as e:
            logging.error("falha na autenticacao %s", e)
            raise NotImplementedError("visualizar LOG") from e

    def req_get(self, uri, listar: bool = False) -> Response:
        logging.debug('%s "GET %s"', self.hashicorp_uri, uri)
        if listar:
            url = f"{self.hashicorp_uri}{uri}?list=true"
        else:
            url = f"{self.hashicorp_uri}{uri}"
        return requests.get(
            url,
            headers={"X-Vault-Token": self._token, "Accept": "application/json"},
            timeout=5.0,
        )

    def req_post(self, uri, json_object) -> Response:
        logging.debug('%s "POST %s"', self.hashicorp_uri, uri)
        url = f"{self.hashicorp_uri}{uri}"
        return requests.post(
            url,
            data=json_object,
            headers={"X-Vault-Token": self._token, "Content-Type": "application/json", "Accept": "application/json"},
            timeout=5.0,
        )

    def get_policy(self, name: str) -> Response:
        uri = f"/v1/sys/policy/{name}"
        return self.req_get(uri)

    def get_secret_kv(self, kv: str, name: str, version: int = 0, metadata: bool = False) -> Response:
        uri = f"/v1/{kv}/data/{name}"
        if metadata:
            uri = f"/v1/{kv}/metadata/{name}"
        if version > 0:
            uri = f"{uri}?version={version}"

        return self.req_get(uri)

    def set_secret_kv(self, kv: str, name: str, payload: dict, metadata: bool = False) -> Response:
        json_object = json.dumps(payload, indent=4)
        uri = f"/v1/{kv}/data/{name}"
        if metadata:
            uri = f"/v1/{kv}/metadata/{name}"
        return self.req_post(uri, json_object)

    def read_current_certificate(self, current_cert_name: str) -> Response:
        """recuperar um certificado pelo nome"""
        logging.info("recuperar um certificado pelo nome %s", current_cert_name)
        api_uri = f"/v1/auth/cert/certs/{current_cert_name}"
        return self.req_get(api_uri)

    def gerar_certificado(self, crt_info: dict[str, str]) -> Response:
        """gera um novo certificado"""
        logging.info("gerando um novo certificado")
        api_uri = f"/v1/{self._conf.pki_mount}/issue/{self._conf.pki_rolename}"
        common_name = f"{crt_info['sigla']}.{crt_info['ambiente']}.{self._conf.pki_rolename}"
        payload = {
            "common_name": common_name,
            "ttl": self._conf.pki_default_ttl,
            "format": self._conf.pki_default_format,
        }
        json_obj = json.dumps(payload, indent=4)
        return self.req_post(uri=api_uri, json_object=json_obj)

    def cadatrar_novo_certificado_auth(
        self, inssue_crt: dict[str, str], crt_info: dict[str, str], current_crt: dict[str, str]
    ) -> Response:
        """cadastra o certificado no auth"""
        logging.info("cadastrando o certificado no auth")
        full_new_cert = inssue_crt["certificate"] + "\n" + inssue_crt["private_key"]
        display_name = f"{crt_info['sigla']}-{crt_info['ambiente']}"
        api_uri = f"/v1/auth/cert/certs/{display_name}"
        payload = {
            "certificate": full_new_cert,
            "display_name": display_name,
            "token_bound_cidrs": current_crt["token_bound_cidrs"],
            "token_policies": current_crt["token_policies"],
            "token_ttl": "4h",
            "token_max_ttl": "4h",
        }
        json_obj = json.dumps(payload, indent=4)
        return self.req_post(uri=api_uri, json_object=json_obj)

    def get_version_kv(self, crt_info: dict[str, str]) -> int:
        """recuperar a versao do segredo para poder ter o controle de versao"""
        name = f"AUTHS/{crt_info['sigla']}-{crt_info['ambiente']}"
        exists_kv = self.get_secret_kv(kv="certificados", name=name)
        if exists_kv.status_code == 200:
            logging.info("KV existente v%s", exists_kv.json()["data"]["metadata"]["version"])
            return exists_kv.json()["data"]["metadata"]["version"] + 1

        logging.info("KV inexistente v0")
        return 1

    def set_new_version_kv(self, inssue_crt: dict[str, str], crt_info: dict[str, str]) -> Response:
        """cadastra o certificado no KV"""
        logging.info("cadastrando o certificado no KV")
        version = self.get_version_kv(crt_info=crt_info)
        name = f"AUTHS/{crt_info['sigla']}-{crt_info['ambiente']}?version={str(version)}"
        payload = {"data": inssue_crt}

        return self.set_secret_kv(kv="certificados", name=name, payload=payload)

    def set_metadata_kv(self, metadata_info: dict[str, str]) -> Response:
        """cadastra metadata no certificado no KV"""
        logging.info("cadastrando metadata no certificado no KV")

        name = f"AUTHS/{metadata_info['sigla']}-{metadata_info['ambiente']}"
        payload = {"custom_metadata": metadata_info}

        return self.set_secret_kv(kv="certificados", name=name, payload=payload, metadata=True)
