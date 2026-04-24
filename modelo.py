# modelo.py
# Classe principal do sistema, representa cada funcionário cadastrado

import uuid
from datetime import datetime


class Funcionario:
    """Representa um funcionário da empresa."""

    def __init__(self, nome: str, cargo: str, departamento: str, salario: float, email: str, func_id: str = None):
        # gera um ID curto caso não venha um já pronto (ex: ao carregar do arquivo)
        self.id = func_id if func_id else str(uuid.uuid4())[:8].upper()
        self.nome = nome
        self.cargo = cargo
        self.departamento = departamento
        self.salario = salario
        self.email = email
        self.data_admissao = datetime.now().strftime("%d/%m/%Y")

    def to_dict(self) -> dict:
        """Transforma o objeto em dicionário para salvar no JSON."""
        return {
            "id": self.id,
            "nome": self.nome,
            "cargo": self.cargo,
            "departamento": self.departamento,
            "salario": self.salario,
            "email": self.email,
            "data_admissao": self.data_admissao,
        }

    @classmethod
    def from_dict(cls, dados: dict):
        """Recria um objeto Funcionario a partir dos dados salvos."""
        obj = cls(
            nome=dados["nome"],
            cargo=dados["cargo"],
            departamento=dados["departamento"],
            salario=dados["salario"],
            email=dados["email"],
            func_id=dados["id"],
        )
        obj.data_admissao = dados.get("data_admissao", obj.data_admissao)
        return obj

    def __repr__(self):
        return f"Funcionario(id={self.id}, nome={self.nome}, cargo={self.cargo})"
