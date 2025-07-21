import interface
from dotenv import load_dotenv
import Funcoes.database as db

if __name__ == "__main__":
    load_dotenv()
    db.criar_tabela_ocorrencias()
    interface.interface()