
# main.py - Ponto de entrada do sistema
# Execute esse arquivo para iniciar o sistema (Só rodar no terminal indo até a pasta que ta salvo os arquivos)

# Verifica se o CustomTkinter está instalado antes de tentar rodar
try:
    import customtkinter
except ImportError:
    print("=" * 55)
    print("  ERRO: CustomTkinter não está instalado.")
    print("  Para instalar, execute no terminal:")
    print("  pip install customtkinter")
    print("=" * 55)
    exit(1)

# Importa e inicia a aplicação
from app import App

if __name__ == "__main__":
    print("Iniciando SistemaCorp...")
    aplicacao = App()
    aplicacao.mainloop()
