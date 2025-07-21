# Funcoes/database.py (versão com reabertura que mantém a assinatura)

import sqlite3
from datetime import datetime

DB_NAME = "ocorrencias.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def criar_tabela_ocorrencias():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patds (
        id INTEGER PRIMARY KEY AUTOINCREMENT, saram TEXT, nome_completo TEXT,
        nome_guerra TEXT NOT NULL, ocorrencia_gerada TEXT NOT NULL, status TEXT NOT NULL,
        data_abertura TEXT, data_conclusao TEXT, caminho_assinatura TEXT
    )""")
    try:
        cursor.execute("ALTER TABLE patds ADD COLUMN caminho_assinatura TEXT;")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def adicionar_ocorrencia(saram, nome_completo, nome_guerra, texto_extraido):
    conn = conectar()
    cursor = conn.cursor()
    data_abertura = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO patds (saram, nome_completo, nome_guerra, ocorrencia_gerada, status, data_abertura)
    VALUES (?, ?, ?, ?, 'Em Aberto', ?)
    """, (saram, nome_completo, nome_guerra, texto_extraido, data_abertura))
    conn.commit()
    conn.close()

def listar_ocorrencias_por_status(status: str):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, saram, nome_completo, nome_guerra, ocorrencia_gerada, status, data_abertura, data_conclusao, caminho_assinatura FROM patds WHERE status = ? ORDER BY id DESC", (status,))
    ocorrencias = cursor.fetchall()
    conn.close()
    return ocorrencias

def buscar_ocorrencia_por_id(patd_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, saram, nome_completo, nome_guerra, ocorrencia_gerada, status, data_abertura, data_conclusao, caminho_assinatura FROM patds WHERE id = ?", (patd_id,))
    ocorrencia = cursor.fetchone()
    conn.close()
    return ocorrencia

def atualizar_ocorrencia(patd_id, texto_ocorrencia):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE patds SET ocorrencia_gerada = ? WHERE id = ?", (texto_ocorrencia, patd_id))
    conn.commit()
    conn.close()
    
def atualizar_caminho_assinatura(patd_id, caminho_assinatura):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE patds SET caminho_assinatura = ? WHERE id = ?", (caminho_assinatura, patd_id))
    conn.commit()
    conn.close()

def fechar_ocorrencia(patd_id):
    conn = conectar()
    cursor = conn.cursor()
    data_conclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE patds SET status = 'Concluída', data_conclusao = ? WHERE id = ?", (data_conclusao, patd_id))
    conn.commit()
    conn.close()

def reabrir_ocorrencia(patd_id):
    """Altera o status para 'Em Aberto' e limpa a data de conclusão, MANTENDO a assinatura."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE patds SET status = 'Em Aberto', data_conclusao = NULL WHERE id = ?", (patd_id,))
    conn.commit()
    conn.close()

def remover_ocorrencia(patd_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patds WHERE id = ?", (patd_id,))
    conn.commit()
    conn.close()