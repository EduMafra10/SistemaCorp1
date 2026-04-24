# app.py
# Interface gráfica do sistema, feita com CustomTkinter

import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk

from modelo import Funcionario
from repositorio import Repositorio
from utils import (
    DEPARTAMENTOS,
    formatar_salario,
    truncar_texto,
    validar_email,
    validar_nome,
    validar_salario,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# cores usadas em toda a interface
CORES = {
    "fundo":        "#0f1117",
    "painel":       "#1a1d27",
    "card":         "#22263a",
    "borda":        "#2e3250",
    "primaria":     "#4f6ef7",
    "primaria_hov": "#6b85fa",
    "sucesso":      "#34d399",
    "perigo":       "#f87171",
    "aviso":        "#fbbf24",
    "texto":        "#e2e8f0",
    "texto_dim":    "#94a3b8",
    "destaque":     "#818cf8",
}


class App(ctk.CTk):
    """Janela raiz da aplicação — controla a navegação entre telas."""

    def __init__(self):
        super().__init__()

        self.title("SistemaCorp — Gestão de Funcionários")
        self.geometry("1100x680")
        self.minsize(900, 600)
        self.configure(fg_color=CORES["fundo"])

        self.repo = Repositorio()

        self.container = ctk.CTkFrame(self, fg_color=CORES["fundo"])
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.telas: dict[str, ctk.CTkFrame] = {}

        self.mostrar_tela("TelaInicial")

    def mostrar_tela(self, nome_tela: str, **kwargs):
        mapa = {
            "TelaInicial": TelaInicial,
            "TelaListar":  TelaListar,
            "TelaCadastro": TelaCadastro,
            "TelaEditar":  TelaEditar,
            "TelaBuscar":  TelaBuscar,
            "TelaDashboard": TelaDashboard,
        }

        # recria telas dinâmicas para sempre mostrar dados atualizados
        if nome_tela in ("TelaListar", "TelaEditar", "TelaBuscar", "TelaDashboard", "TelaCadastro"):
            if nome_tela in self.telas:
                self.telas[nome_tela].destroy()
                del self.telas[nome_tela]

        if nome_tela not in self.telas:
            classe = mapa[nome_tela]
            frame = classe(self.container, self, **kwargs)
            frame.grid(row=0, column=0, sticky="nsew")
            self.telas[nome_tela] = frame

        self.telas[nome_tela].tkraise()


# funções auxiliares para criar widgets com estilo padrão

def criar_botao(parent, texto, comando, cor=None, largura=160, altura=38):
    cor = cor or CORES["primaria"]
    return ctk.CTkButton(
        parent,
        text=texto,
        command=comando,
        fg_color=cor,
        hover_color=CORES["primaria_hov"],
        corner_radius=8,
        width=largura,
        height=altura,
        font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
    )


def criar_entrada(parent, placeholder="", largura=280):

    return ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        width=largura,
        height=38,
        corner_radius=8,
        fg_color=CORES["card"],
        border_color=CORES["borda"],
        text_color=CORES["texto"],
        placeholder_text_color=CORES["texto_dim"],
        font=ctk.CTkFont(family="Segoe UI", size=13),
    )


def criar_label(parent, texto, tamanho=13, cor=None, negrito=False):
    peso = "bold" if negrito else "normal"
    return ctk.CTkLabel(
        parent,
        text=texto,
        font=ctk.CTkFont(family="Segoe UI", size=tamanho, weight=peso),
        text_color=cor or CORES["texto"],
    )


class TelaInicial(ctk.CTkFrame):

    def __init__(self, parent, app: App):
        super().__init__(parent, fg_color=CORES["fundo"])
        self.app = app
        self._construir()

    def _construir(self):
        topo = ctk.CTkFrame(self, fg_color=CORES["painel"], corner_radius=0, height=70)
        topo.pack(fill="x")
        criar_label(topo, "⚙  SistemaCorp", tamanho=22, cor=CORES["primaria"], negrito=True).pack(
            side="left", padx=30, pady=18
        )
        criar_label(topo, "Gestão de Funcionários", tamanho=13, cor=CORES["texto_dim"]).pack(
            side="left", pady=18
        )

        centro = ctk.CTkFrame(self, fg_color=CORES["fundo"])
        centro.pack(fill="both", expand=True, padx=60, pady=40)

        criar_label(centro, "O que você quer fazer?", tamanho=17, negrito=True).pack(pady=(0, 30))

        grid = ctk.CTkFrame(centro, fg_color=CORES["fundo"])
        grid.pack()

        opcoes = [
            ("📋  Listar Funcionários",   CORES["primaria"],  lambda: self.app.mostrar_tela("TelaListar")),
            ("➕  Cadastrar Funcionário", CORES["sucesso"],   lambda: self.app.mostrar_tela("TelaCadastro")),
            ("🔍  Buscar Funcionário",    CORES["aviso"],     lambda: self.app.mostrar_tela("TelaBuscar")),
            ("📊  Dashboard / Relatório", CORES["destaque"],  lambda: self.app.mostrar_tela("TelaDashboard")),
        ]

        for i, (texto, cor, cmd) in enumerate(opcoes):
            col = i % 2
            lin = i // 2
            btn = ctk.CTkButton(
                grid,
                text=texto,
                command=cmd,
                fg_color=CORES["card"],
                hover_color=CORES["borda"],
                border_color=cor,
                border_width=2,
                corner_radius=12,
                width=220,
                height=90,
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                text_color=cor,
            )
            btn.grid(row=lin, column=col, padx=14, pady=14)

        total = len(self.app.repo.listar_todos())
        criar_label(
            centro,
            f"Total de funcionários cadastrados: {total}",
            tamanho=12,
            cor=CORES["texto_dim"],
        ).pack(pady=20)


class TelaListar(ctk.CTkFrame):
    """Exibe todos os funcionários em uma tabela."""

    COLUNAS = ("ID", "Nome", "Cargo", "Departamento", "Salário", "E-mail", "Admissão")

    def __init__(self, parent, app: App):
        super().__init__(parent, fg_color=CORES["fundo"])
        self.app = app
        self._construir()

    def _construir(self):
        self._cabecalho("📋  Lista de Funcionários")

        barra = ctk.CTkFrame(self, fg_color=CORES["painel"], height=55)
        barra.pack(fill="x", padx=20, pady=(0, 10))

        criar_botao(barra, "← Voltar", lambda: self.app.mostrar_tela("TelaInicial"),
                    cor="#374151").pack(side="left", padx=10, pady=10)
        criar_botao(barra, "✏ Editar selecionado", self._editar_selecionado,
                    cor=CORES["aviso"]).pack(side="left", padx=5, pady=10)
        criar_botao(barra, "🗑 Excluir selecionado", self._excluir_selecionado,
                    cor=CORES["perigo"]).pack(side="left", padx=5, pady=10)
        criar_botao(barra, "↻ Atualizar", self._atualizar_lista,
                    cor=CORES["sucesso"]).pack(side="right", padx=10, pady=10)

        frame_tabela = ctk.CTkFrame(self, fg_color=CORES["painel"], corner_radius=10)
        frame_tabela.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Custom.Treeview",
            background=CORES["card"],
            fieldbackground=CORES["card"],
            foreground=CORES["texto"],
            rowheight=32,
            borderwidth=0,
            font=("Segoe UI", 12),
        )
        estilo.configure(
            "Custom.Treeview.Heading",
            background=CORES["painel"],
            foreground=CORES["destaque"],
            font=("Segoe UI", 12, "bold"),
            relief="flat",
        )
        estilo.map("Custom.Treeview", background=[("selected", CORES["primaria"])])

        scroll_y = ttk.Scrollbar(frame_tabela, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        self.tabela = ttk.Treeview(
            frame_tabela,
            columns=self.COLUNAS,
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=scroll_y.set,
        )
        scroll_y.config(command=self.tabela.yview)

        larguras = {"ID": 80, "Nome": 180, "Cargo": 150, "Departamento": 120,
                    "Salário": 110, "E-mail": 200, "Admissão": 100}
        for col in self.COLUNAS:
            self.tabela.heading(col, text=col)
            self.tabela.column(col, width=larguras.get(col, 120), anchor="center")

        self.tabela.pack(fill="both", expand=True, padx=5, pady=5)
        self._popular_tabela()

    def _cabecalho(self, titulo):
        topo = ctk.CTkFrame(self, fg_color=CORES["painel"], corner_radius=0, height=60)
        topo.pack(fill="x")
        criar_label(topo, titulo, tamanho=18, negrito=True).pack(side="left", padx=25, pady=16)

    def _popular_tabela(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for func in self.app.repo.listar_todos():
            self.tabela.insert(
                "",
                "end",
                iid=func.id,
                values=(
                    func.id,
                    truncar_texto(func.nome, 22),
                    truncar_texto(func.cargo, 18),
                    func.departamento,
                    formatar_salario(func.salario),
                    truncar_texto(func.email, 25),
                    func.data_admissao,
                ),
            )

    def _get_id_selecionado(self):
        sel = self.tabela.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um funcionário na lista.")
            return None
        return sel[0]

    def _editar_selecionado(self):
        func_id = self._get_id_selecionado()
        if func_id:
            self.app.mostrar_tela("TelaEditar", func_id=func_id)

    def _excluir_selecionado(self):
        func_id = self._get_id_selecionado()
        if not func_id:
            return
        func = self.app.repo.buscar_por_id(func_id)
        if not messagebox.askyesno(
            "Confirmar exclusão",
            f"Tem certeza que deseja excluir '{func.nome}'?\nEssa ação não pode ser desfeita.",
        ):
            return
        if self.app.repo.remover(func_id):
            messagebox.showinfo("Sucesso", "Funcionário excluído com sucesso!")
            self._atualizar_lista()
        else:
            messagebox.showerror("Erro", "Não foi possível excluir o funcionário.")

    def _atualizar_lista(self):
        self._popular_tabela()



# ---------------------------------------------------------------
# TELA CADASTRO
# ---------------------------------------------------------------

class TelaCadastro(ctk.CTkFrame):

    def __init__(self, parent, app: App):
        super().__init__(parent, fg_color=CORES["fundo"])
        self.app = app
        self._construir()

    def _construir(self):
        topo = ctk.CTkFrame(self, fg_color=CORES["painel"], corner_radius=0, height=60)
        topo.pack(fill="x")
        criar_label(topo, "➕  Cadastrar Novo Funcionário", tamanho=18, negrito=True).pack(
            side="left", padx=25, pady=16
        )

        form = ctk.CTkFrame(self, fg_color=CORES["painel"], corner_radius=14)
        form.pack(padx=80, pady=30, fill="both", expand=True)

        campos_label = [
            ("Nome completo *", "Ex: João da Silva"),
            ("Cargo *", "Ex: Analista de Sistemas"),
            ("E-mail *", "joao@empresa.com"),
            ("Salário (R$) *", "Ex: 5000.00"),
        ]

        self.entradas: dict[str, ctk.CTkEntry] = {}

        for i, (label, ph) in enumerate(campos_label):
            criar_label(form, label, tamanho=13, cor=CORES["texto_dim"]).grid(
                row=i * 2, column=0, sticky="w", padx=30, pady=(20, 2)
            )
            entrada = criar_entrada(form, placeholder=ph, largura=340)
            entrada.grid(row=i * 2 + 1, column=0, sticky="w", padx=30, pady=(0, 4))
            chave = label.split(" ")[0].lower()
            self.entradas[chave] = entrada

        criar_label(form, "Departamento *", tamanho=13, cor=CORES["texto_dim"]).grid(
            row=8, column=0, sticky="w", padx=30, pady=(20, 2)
        )
        self.combo_depto = ctk.CTkComboBox(
            form,
            values=DEPARTAMENTOS,
            width=340,
            height=38,
            fg_color=CORES["card"],
            border_color=CORES["borda"],
            button_color=CORES["primaria"],
            dropdown_fg_color=CORES["card"],
            text_color=CORES["texto"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self.combo_depto.set(DEPARTAMENTOS[0])
        self.combo_depto.grid(row=9, column=0, sticky="w", padx=30, pady=(0, 4))

        barra_btn = ctk.CTkFrame(form, fg_color="transparent")
        barra_btn.grid(row=10, column=0, pady=30, padx=30, sticky="w")

        criar_botao(barra_btn, "✓  Salvar", self._salvar, cor=CORES["sucesso"]).pack(side="left", padx=(0, 12))
        criar_botao(barra_btn, "← Voltar", lambda: self.app.mostrar_tela("TelaInicial"),
                    cor="#374151").pack(side="left")

    def _salvar(self):
        nome = self.entradas["nome"].get().strip()
        cargo = self.entradas["cargo"].get().strip()
        email = self.entradas["e-mail"].get().strip()
        salario_str = self.entradas["salário"].get().strip()
        departamento = self.combo_depto.get()

        if not validar_nome(nome):
            messagebox.showerror("Erro", "O nome precisa ter pelo menos 3 caracteres.")
            return
        if not cargo:
            messagebox.showerror("Erro", "Informe o cargo do funcionário.")
            return
        if not validar_email(email):
            messagebox.showerror("Erro", "E-mail inválido. Use o formato: nome@dominio.com")
            return
        ok, salario = validar_salario(salario_str)
        if not ok:
            messagebox.showerror("Erro", "Salário inválido. Use um número positivo.")
            return

        novo = Funcionario(nome=nome, cargo=cargo, departamento=departamento,
                           salario=salario, email=email)

        if not self.app.repo.adicionar(novo):
            messagebox.showerror("Erro", "Já existe um funcionário com esse e-mail.")
            return

        messagebox.showinfo("Sucesso", f"Funcionário '{nome}' cadastrado!\nID gerado: {novo.id}")
        self.app.mostrar_tela("TelaListar")


class TelaEditar(ctk.CTkFrame):

    def __init__(self, parent, app: App, func_id: str = ""):
        super().__init__(parent, fg_color=CORES["fundo"])
        self.app = app
        self.func = app.repo.buscar_por_id(func_id)
        if not self.func:
            messagebox.showerror("Erro", "Funcionário não encontrado.")
            app.mostrar_tela("TelaListar")
            return
        self._construir()

    def _construir(self):
        topo = ctk.CTkFrame(self, fg_color=CORES["painel"], corner_radius=0, height=60)
        topo.pack(fill="x")
        criar_label(topo, f"✏  Editar — {self.func.nome}", tamanho=17, negrito=True).pack(
            side="left", padx=25, pady=16
        )
        criar_label(topo, f"ID: {self.func.id}", tamanho=12, cor=CORES["texto_dim"]).pack(
            side="right", padx=25, pady=16
        )

        form = ctk.CTkFrame(self, fg_color=CORES["painel"], corner_radius=14)
        form.pack(padx=80, pady=30, fill="both", expand=True)

        campos = [
            ("Nome completo", self.func.nome),
            ("Cargo", self.func.cargo),
            ("E-mail", self.func.email),
            ("Salário (R$)", str(self.func.salario)),
        ]

        self.entradas: dict[str, ctk.CTkEntry] = {}
        for i, (label, valor) in enumerate(campos):
            criar_label(form, label, tamanho=13, cor=CORES["texto_dim"]).grid(
                row=i * 2, column=0, sticky="w", padx=30, pady=(20, 2)
            )
            entrada = criar_entrada(form, largura=340)
            entrada.insert(0, valor)
            entrada.grid(row=i * 2 + 1, column=0, sticky="w", padx=30, pady=(0, 4))
            self.entradas[label.split(" ")[0].lower()] = entrada

        criar_label(form, "Departamento", tamanho=13, cor=CORES["texto_dim"]).grid(
            row=8, column=0, sticky="w", padx=30, pady=(20, 2)
        )
        self.combo_depto = ctk.CTkComboBox(
            form, values=DEPARTAMENTOS, width=340, height=38,
            fg_color=CORES["card"], border_color=CORES["borda"],
            button_color=CORES["primaria"], dropdown_fg_color=CORES["card"],
            text_color=CORES["texto"], font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self.combo_depto.set(self.func.departamento)
        self.combo_depto.grid(row=9, column=0, sticky="w", padx=30, pady=(0, 4))

        barra = ctk.CTkFrame(form, fg_color="transparent")
        barra.grid(row=10, column=0, pady=30, padx=30, sticky="w")
        criar_botao(barra, "✓  Salvar alterações", self._salvar, cor=CORES["sucesso"]).pack(side="left", padx=(0, 12))
        criar_botao(barra, "← Voltar", lambda: self.app.mostrar_tela("TelaListar"), cor="#374151").pack(side="left")

    def _salvar(self):
        nome = self.entradas["nome"].get().strip()
        cargo = self.entradas["cargo"].get().strip()
        email = self.entradas["e-mail"].get().strip()
        salario_str = self.entradas["salário"].get().strip()
        departamento = self.combo_depto.get()

        if not validar_nome(nome):
            messagebox.showerror("Erro", "Nome inválido.")
            return
        if not validar_email(email):
            messagebox.showerror("Erro", "E-mail inválido.")
            return
        ok, salario = validar_salario(salario_str)
        if not ok:
            messagebox.showerror("Erro", "Salário inválido.")
            return


        novos_dados = {
            "nome": nome, "cargo": cargo, "email": email,
            "salario": salario, "departamento": departamento,
        }
        if self.app.repo.atualizar(self.func.id, novos_dados):
            messagebox.showinfo("Sucesso", "Funcionário atualizado com sucesso!")
            self.app.mostrar_tela("TelaListar")
        else:
            messagebox.showerror("Erro", "Não foi possível salvar as alterações.")



class TelaBuscar(ctk.CTkFrame):

    def __init__(self, parent, app: App):
        super().__init__(parent, fg_color=CORES["fundo"])
        self.app = app
        self._construir()

    def _construir(self):
        topo = ctk.CTkFrame(self, fg_color=CORES["painel"], corner_radius=0, height=60)
        topo.pack(fill="x")
        criar_label(topo, "🔍  Buscar Funcionário", tamanho=18, negrito=True).pack(side="left", padx=25, pady=16)
        criar_botao(topo, "← Voltar", lambda: self.app.mostrar_tela("TelaInicial"),
                    cor="#374151", largura=120).pack(side="right", padx=20, pady=10)

        painel_busca = ctk.CTkFrame(self, fg_color=CORES["painel"], corner_radius=10)
        painel_busca.pack(fill="x", padx=20, pady=14)

        criar_label(painel_busca, "Nome:", tamanho=13).grid(row=0, column=0, padx=(20, 8), pady=16)
        self.entrada_nome = criar_entrada(painel_busca, placeholder="Digite parte do nome...", largura=260)
        self.entrada_nome.grid(row=0, column=1, padx=(0, 16), pady=16)

        criar_label(painel_busca, "Departamento:", tamanho=13).grid(row=0, column=2, padx=(0, 8), pady=16)
        self.combo_depto = ctk.CTkComboBox(
            painel_busca, values=["Todos"] + DEPARTAMENTOS, width=200, height=38,
            fg_color=CORES["card"], border_color=CORES["borda"], button_color=CORES["primaria"],
            dropdown_fg_color=CORES["card"], text_color=CORES["texto"],
        )
        self.combo_depto.set("Todos")
        self.combo_depto.grid(row=0, column=3, padx=(0, 16), pady=16)

        criar_botao(painel_busca, "🔍 Buscar", self._buscar, cor=CORES["primaria"]).grid(
            row=0, column=4, padx=(0, 20), pady=16
        )

        frame_res = ctk.CTkFrame(self, fg_color=CORES["painel"], corner_radius=10)
        frame_res.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        estilo = ttk.Style()
        estilo.configure("Busca.Treeview", background=CORES["card"], fieldbackground=CORES["card"],
                         foreground=CORES["texto"], rowheight=30, font=("Segoe UI", 12))
        estilo.configure("Busca.Treeview.Heading", background=CORES["painel"],
                         foreground=CORES["destaque"], font=("Segoe UI", 12, "bold"), relief="flat")
        estilo.map("Busca.Treeview", background=[("selected", CORES["primaria"])])

        colunas = ("ID", "Nome", "Cargo", "Departamento", "Salário", "E-mail")
        self.tabela = ttk.Treeview(frame_res, columns=colunas, show="headings", style="Busca.Treeview")
        larguras = {"ID": 80, "Nome": 200, "Cargo": 160, "Departamento": 130, "Salário": 120, "E-mail": 220}
        for col in colunas:
            self.tabela.heading(col, text=col)
            self.tabela.column(col, width=larguras[col], anchor="center")

        sb = ttk.Scrollbar(frame_res, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tabela.pack(fill="both", expand=True, padx=5, pady=5)

        self.label_resultado = criar_label(frame_res, "", tamanho=12, cor=CORES["texto_dim"])
        self.label_resultado.pack(pady=6)

        self._buscar()

    def _buscar(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        nome_busca = self.entrada_nome.get().strip()
        depto_busca = self.combo_depto.get()

        if nome_busca:
            resultados = self.app.repo.buscar_por_nome(nome_busca)
        else:
            resultados = self.app.repo.listar_todos()

        if depto_busca != "Todos":
            resultados = [f for f in resultados if f.departamento == depto_busca]

        for func in resultados:
            self.tabela.insert("", "end", values=(
                func.id, func.nome, func.cargo,
                func.departamento, formatar_salario(func.salario), func.email,
            ))

        qtd = len(resultados)
        self.label_resultado.configure(text=f"{qtd} funcionário(s) encontrado(s).")


class TelaDashboard(ctk.CTkFrame):

    def __init__(self, parent, app: App):
        super().__init__(parent, fg_color=CORES["fundo"])
        self.app = app
        self._construir()

    def _construir(self):
        topo = ctk.CTkFrame(self, fg_color=CORES["painel"], corner_radius=0, height=60)
        topo.pack(fill="x")
        criar_label(topo, "📊  Dashboard — Visão Geral", tamanho=18, negrito=True).pack(side="left", padx=25, pady=16)
        criar_botao(topo, "← Voltar", lambda: self.app.mostrar_tela("TelaInicial"),
                    cor="#374151", largura=120).pack(side="right", padx=20, pady=10)

        stats = self.app.repo.estatisticas()
        todos = self.app.repo.listar_todos()

        row_cards = ctk.CTkFrame(self, fg_color=CORES["fundo"])
        row_cards.pack(fill="x", padx=20, pady=20)

        metricas = [
            ("Total de funcionários", str(stats["total"]),          CORES["primaria"]),
            ("Média salarial",        formatar_salario(stats["media_salarial"]), CORES["sucesso"]),
            ("Maior salário",         formatar_salario(stats["maior_salario"]),  CORES["aviso"]),
            ("Menor salário",         formatar_salario(stats["menor_salario"]),  CORES["destaque"]),
        ]

        for titulo, valor, cor in metricas:
            card = ctk.CTkFrame(row_cards, fg_color=CORES["card"], corner_radius=12, width=200, height=90)
            card.pack(side="left", padx=10, pady=6, expand=True, fill="x")
            criar_label(card, titulo, tamanho=12, cor=CORES["texto_dim"]).pack(pady=(14, 2))
            criar_label(card, valor, tamanho=16, cor=cor, negrito=True).pack()

        criar_label(self, "Funcionários por Departamento", tamanho=14, negrito=True,
                    cor=CORES["texto_dim"]).pack(padx=20, pady=(10, 6), anchor="w")

        frame_depto = ctk.CTkFrame(self, fg_color=CORES["painel"], corner_radius=10)
        frame_depto.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # agrupa por departamento num dicionário
        resumo: dict[str, dict] = {}
        for func in todos:
            dep = func.departamento
            if dep not in resumo:
                resumo[dep] = {"qtd": 0, "total_sal": 0.0}
            resumo[dep]["qtd"] += 1
            resumo[dep]["total_sal"] += func.salario


        estilo = ttk.Style()
        estilo.configure("Dash.Treeview", background=CORES["card"], fieldbackground=CORES["card"],
                         foreground=CORES["texto"], rowheight=30, font=("Segoe UI", 12))
        estilo.configure("Dash.Treeview.Heading", background=CORES["painel"],
                         foreground=CORES["destaque"], font=("Segoe UI", 12, "bold"), relief="flat")
        estilo.map("Dash.Treeview", background=[("selected", CORES["primaria"])])

        cols = ("Departamento", "Qtd. Funcionários", "Média Salarial", "Total Folha")
        tabela = ttk.Treeview(frame_depto, columns=cols, show="headings", style="Dash.Treeview")
        for col in cols:
            tabela.heading(col, text=col)
            tabela.column(col, width=200, anchor="center")

        for dep, dados in sorted(resumo.items()):
            media = dados["total_sal"] / dados["qtd"]
            tabela.insert("", "end", values=(
                dep, dados["qtd"],
                formatar_salario(media),
                formatar_salario(dados["total_sal"]),
            ))

        sb = ttk.Scrollbar(frame_depto, orient="vertical", command=tabela.yview)
        tabela.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tabela.pack(fill="both", expand=True, padx=5, pady=5)


# ---------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------

if __name__ == "__main__":
    app = App()
    app.mainloop()
