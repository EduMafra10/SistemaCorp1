# utils.py
# Funções de validação e formatação usadas em vários lugares do sistema

import re


DEPARTAMENTOS = ["TI", "Financeiro", "Marketing", "RH", "Operações", "Jurídico", "Comercial"]


def validar_email(email: str) -> bool:
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return bool(re.match(padrao, email.strip()))


def validar_salario(valor_str: str) -> tuple[bool, float]:
    # aceita vírgula ou ponto como separador
    valor_str = valor_str.replace(",", ".")
    try:
        valor = float(valor_str)
        if valor <= 0:
            return False, 0.0
        return True, round(valor, 2)
    except ValueError:
        return False, 0.0


def validar_nome(nome: str) -> bool:
    return len(nome.strip()) >= 3


def formatar_salario(valor: float) -> str:
    # converte para o formato brasileiro: R$ 7.500,00
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def truncar_texto(texto: str, limite: int = 25) -> str:
    if len(texto) <= limite:
        return texto
    return texto[: limite - 3] + "..."

