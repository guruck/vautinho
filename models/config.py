"""modelo dos dados de configuracao"""
from pydantic import BaseModel


class VaultConfig(BaseModel):
    """se necessario adicionar campos em config.ini,
    aqui deve ser alterado também para consumo do dado
    """

    uri: str
    port: str
    user: str
    passwd: str
    pki_mount: str
    pki_rolename: str
    pki_default_format: str
    pki_default_ttl: str
    pki_ca_cert: str
    pki_int_cert: str
    pki_key: str
    today: str
    str_path_src: str
