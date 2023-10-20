"""modelo dos dados de configuracao"""
from pydantic import BaseModel


class TicketConfig(BaseModel):
    """se necessario adicionar campos em config.ini,
    aqui deve ser alterado também para consumo do dado
    """

    solicitacao: str
    responsavel: str
    nome_responsavel: str
    nick_responsavel: str
    sigla: str
    depto: str
    grupo_suporte: str
    extensao: str
    status: str
    balanceador: str
    ambiente: str
    comunidade: str
