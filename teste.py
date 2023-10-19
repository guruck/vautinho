"""teste de autenticacao"""
import hvac
import requests
import json


DEFAULT_URL = "http://127.0.0.1:8200"


def get_vault_client(vault_url=DEFAULT_URL):
    """
    Instantiates a hvac / vault client.
    :param vault_url: string, protocol + address + port for the vault service
    :param certs: tuple, Optional tuple of self-signed certs to use for verification
            with hvac's requests adapater.
    :return: hvac.Client
    """
    print("Retrieving a vault (hvac) client...")

    # vault_client = hvac.Client(url=vault_url, cert=certs)

    vault_client = hvac.Client(url=vault_url)
    login_response = vault_client.auth.userpass.login("teste", "Teste$123")
    if not vault_client.is_authenticated():
        error_msg = "Unable to authenticate to the Vault service"
        raise hvac.exceptions.Unauthorized(error_msg)

    print(login_response["auth"]["client_token"])

    return vault_client


vault_client = get_vault_client(DEFAULT_URL)
current_token = vault_client.auth.token.lookup_self()
token_str = current_token["data"]["id"]
# print(current_token)
# print(current_token["data"]["id"])
# Logout
# vault_client.logout()

# curl --header "X-Vault-Token: ..." http://127.0.0.1:8200/v1/sys/policy/my-policy
url = f"{DEFAULT_URL}/v1/sys/policy/admin"
x = requests.get(url, headers={"X-Vault-Token": token_str, "Accept": "application/json"}, timeout=2.50)
print("-" * 80)
dict_x = x.json()
print("dict_x:", dict_x, type(dict_x))
print("-" * 80)

url = f"{DEFAULT_URL}/v1/secret/data/hello-vault"
x = requests.get(url, headers={"X-Vault-Token": token_str, "Accept": "application/json"}, timeout=2.50)
json_data = json.loads(x.text)
print("json_data:", json_data, type(json_data))
print("-" * 80)

# payload = {"data": {"who": "Spring I/O 18", "foo": "bar", "zip": "zap"}}
# json_object = json.dumps(payload, indent=4)
# print(json_object)

# url = f"{DEFAULT_URL}/v1/secret/data/hello-vault"
# x = requests.post(
#     url,
#     data=json_object,
#     headers={"X-Vault-Token": token_str, "Content-Type": "application/json", "Accept": "application/json"},
#     timeout=2.50,
# )
# json_data = json.loads(x.text)
# print("json_data:", json_data, type(json_data))
# print("-" * 80)

url = f"{DEFAULT_URL}/v1/pki/roles/2023-servers"
x = requests.get(url, headers={"X-Vault-Token": token_str, "Accept": "application/json"}, timeout=2.50)
json_data = json.loads(x.text)
print("json_data:", json_data, type(json_data))
print("-" * 80)

url = f"{DEFAULT_URL}/v1/pki/roles?list=true"
x = requests.get(url, headers={"X-Vault-Token": token_str, "Accept": "application/json"}, timeout=2.50)
json_data = json.loads(x.text)
print("json_data:", json_data, type(json_data))
print("-" * 80)

url = f"{DEFAULT_URL}/v1/pki/issuers?list=true"
x = requests.get(url, headers={"X-Vault-Token": token_str, "Accept": "application/json"}, timeout=2.50)
json_data = json.loads(x.text)
print("json_data:", json_data, type(json_data))
print("-" * 80)

url = f"{DEFAULT_URL}/v1/pki/issuer/root-2024"
x = requests.get(url, headers={"X-Vault-Token": token_str, "Accept": "application/json"}, timeout=2.50)
json_data = json.loads(x.text)
print("json_data:", json_data, type(json_data))
print("-" * 80)

# string_response = json.dumps(x.json().get("data"))

# f = open("demofile2.json", "w")
# f.write(string_response)
# f.close()
