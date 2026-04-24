# repositorio.py
# Cuida de tudo que envolve salvar, buscar e remover funcionários

import json
import os

from modelo import Funcionario

ARQUIVO_DADOS = os.path.join(os.path.dirname(__file__), "dados_funcionarios.json")


class Repositorio:
    """Gerencia a lista de funcionários e persiste os dados em JSON."""

    def __init__(self):
        self._funcionarios: list[Funcionario] = []
        self._carregar_dados()

    # --- arquivo ---

    def _carregar_dados(self):
        if not os.path.exists(ARQUIVO_DADOS):
            # primeira execução: cria alguns registros apenas para usarmos de exemplo nos prints que o professor pediu
            self._popular_dados_iniciais()
            return

        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            try:
                lista = json.load(f)
                self._funcionarios = [Funcionario.from_dict(d) for d in lista]
            except json.JSONDecodeError:
                self._funcionarios = []

    def _salvar_dados(self):
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump([func.to_dict() for func in self._funcionarios], f, ensure_ascii=False, indent=2)

    def _popular_dados_iniciais(self):
        exemplos = [
            Funcionario("Ana Paula Souza", "Desenvolvedora", "TI", 7500.00, "ana.souza@empresa.com"),
            Funcionario("Carlos Eduardo Lima", "Gerente de Projetos", "TI", 9200.00, "carlos.lima@empresa.com"),
            Funcionario("Fernanda Rocha", "Analista Financeiro", "Financeiro", 6800.00, "fernanda.rocha@empresa.com"),
            Funcionario("Marcos Vinícius", "Designer UX", "Marketing", 5900.00, "marcos.vinicius@empresa.com"),
            Funcionario("Juliana Matos", "Recursos Humanos", "RH", 5400.00, "juliana.matos@empresa.com"),
        ]
        self._funcionarios = exemplos
        self._salvar_dados()

    # --- CREATE ---

    def adicionar(self, func: Funcionario) -> bool:
        # impede e-mail duplicado
        if any(f.email.lower() == func.email.lower() for f in self._funcionarios):
            return False
        self._funcionarios.append(func)
        self._salvar_dados()
        return True

    # --- READ ---

    def listar_todos(self) -> list[Funcionario]:
        return list(self._funcionarios)

    def buscar_por_id(self, func_id: str):
        for f in self._funcionarios:
            if f.id == func_id.upper():
                return f
        return None

    def buscar_por_nome(self, termo: str) -> list[Funcionario]:
        termo_lower = termo.lower()
        return [f for f in self._funcionarios if termo_lower in f.nome.lower()]

    def filtrar_por_departamento(self, departamento: str) -> list[Funcionario]:
        return [f for f in self._funcionarios if f.departamento == departamento]

    def listar_departamentos(self) -> list[str]:
        return sorted(set(f.departamento for f in self._funcionarios))

    # --- UPDATE ---

    def atualizar(self, func_id: str, novos_dados: dict) -> bool:
        func = self.buscar_por_id(func_id)
        if not func:
            return False

        # só atualiza os campos que vieram no dicionário
        if "nome" in novos_dados:
            func.nome = novos_dados["nome"]
        if "cargo" in novos_dados:
            func.cargo = novos_dados["cargo"]
        if "departamento" in novos_dados:
            func.departamento = novos_dados["departamento"]
        if "salario" in novos_dados:
            func.salario = novos_dados["salario"]
        if "email" in novos_dados:
            func.email = novos_dados["email"]

        self._salvar_dados()
        return True

    # --- DELETE ---

    def remover(self, func_id: str) -> bool:
        func = self.buscar_por_id(func_id)
        if not func:
            return False
        self._funcionarios.remove(func)
        self._salvar_dados()
        return True

    # --- estatísticas ---

    def estatisticas(self) -> dict:
        if not self._funcionarios:
            return {"total": 0, "media_salarial": 0.0, "maior_salario": 0.0, "menor_salario": 0.0}

        salarios = [f.salario for f in self._funcionarios]
        return {
            "total": len(self._funcionarios),
            "media_salarial": sum(salarios) / len(salarios),
            "maior_salario": max(salarios),
            "menor_salario": min(salarios),
        }
