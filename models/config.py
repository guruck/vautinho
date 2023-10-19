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
    today: str
