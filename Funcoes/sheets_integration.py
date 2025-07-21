# Funcoes/sheets_integration.py (versão com extração de dados corrigida)

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Define os escopos de acesso da API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Carrega as credenciais do arquivo JSON
CREDS = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
CLIENT = gspread.authorize(CREDS)

# --- IMPORTANTE: SUBSTITUA PELO NOME DA SUA PLANILHA ---
NOME_DA_PLANILHA = "Sd"
# ----------------------------------------------------

def find_col_name(df, possible_names):
    for col in df.columns:
        if col.lower() in possible_names:
            return col
    return None

def get_info_by_war_name(nome_guerra: str) -> dict:
    try:
        spreadsheet = CLIENT.open(NOME_DA_PLANILHA)
        worksheet = spreadsheet.sheet1
        
        data = worksheet.get_all_records()
        if not data:
            return {"erro": "A planilha está vazia ou não foi possível ler os registros."}

        df = pd.DataFrame(data)

        # Nomes possíveis para as colunas (em minúsculas)
        col_nome_guerra_names = ['nome de guerra', 'nome_de_guerra']
        col_saram_names = ['saram']
        col_nome_completo_names = ['nome completo', 'nome_completo']

        # Encontra os nomes reais das colunas no DataFrame
        col_nome_guerra = find_col_name(df, col_nome_guerra_names)
        col_saram = find_col_name(df, col_saram_names)
        col_nome_completo = find_col_name(df, col_nome_completo_names)

        if not col_nome_guerra:
            return {"erro": "A coluna 'Nome de Guerra' não foi encontrada na planilha."}

        # Busca pelo nome de guerra (insensível a maiúsculas/minúsculas)
        resultado = df[df[col_nome_guerra].str.lower() == nome_guerra.lower()]
        
        if not resultado.empty:
            militar_info = resultado.iloc[0]
            return {
                "nome_completo": str(militar_info.get(col_nome_completo, "N/A")) if col_nome_completo else "N/A",
                "saram": str(militar_info.get(col_saram, "N/A")) if col_saram else "N/A",
                "nome_guerra": str(militar_info.get(col_nome_guerra, "N/A"))
            }
        else:
            return {"erro": f"Militar com nome de guerra '{nome_guerra}' não encontrado."}
            
    except gspread.exceptions.SpreadsheetNotFound:
        return {"erro": f"A planilha '{NOME_DA_PLANILHA}' não foi encontrada."}
    except Exception as e:
        return {"erro": f"Ocorreu um erro ao acessar a planilha: {e}"}