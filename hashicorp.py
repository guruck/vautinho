"""Classe operacional Vault Hashicorp"""
import hvac
import requests
import logging
import json

from requests.models import Response


class Vault:
    def __init__(self, config):
        self._conf = config
        self._url = f"{self._conf.uri}:{self._conf.port}"
        self._token = ""

    def get_vault_client(self):
        """
        Instantiates a hvac / vault client.
        :param vault_url: string, protocol + address + port for the vault service
        :param certs: tuple, Optional tuple of self-signed certs to use for verification
                with hvac's requests adapater.
        :return: hvac.Client
        """
        print("Retrieving a vault (hvac) client...")

        # vault_client = hvac.Client(url=self._url, cert=certs)
        vault_client = hvac.Client(url=self._url)
        login_response = vault_client.auth.userpass.login(self._conf.user, self._conf.passwd)
        if not vault_client.is_authenticated():
            error_msg = "Unable to authenticate to the Vault service"
            raise hvac.exceptions.Unauthorized(error_msg)

        self._token = login_response["auth"]["client_token"]
        logging.info(self._token)

        return vault_client

    def req_get(self, uri, listar: bool = False) -> Response:
        logging.debug('%s "GET %s"', self._url, uri)
        if listar:
            url = f"{self._url}{uri}?list=true"
        else:
            url = f"{self._url}{uri}"
        return requests.get(
            url,
            headers={"X-Vault-Token": self._token, "Accept": "application/json"},
            timeout=5.0,
        )

    def req_post(self, uri, json_object) -> Response:
        logging.debug('%s "GET %s"', self._url, uri)
        url = f"{self._url}{uri}"
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
