# Funcoes/database.py

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
        data_abertura TEXT, data_conclusao TEXT, caminho_assinatura TEXT, id_oficial INTEGER
    )""")
    try:
        cursor.execute("ALTER TABLE patds ADD COLUMN id_oficial INTEGER;")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def criar_tabela_oficiais():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS oficiais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_completo TEXT NOT NULL,
        nome_guerra TEXT NOT NULL,
        posto_graduacao TEXT NOT NULL,
        caminho_assinatura TEXT
    )""")
    conn.commit()
    conn.close()

def adicionar_oficial(nome_completo, nome_guerra, posto_graduacao, caminho_assinatura):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO oficiais (nome_completo, nome_guerra, posto_graduacao, caminho_assinatura)
    VALUES (?, ?, ?, ?)
    """, (nome_completo, nome_guerra, posto_graduacao, caminho_assinatura))
    conn.commit()
    conn.close()

def editar_oficial(id_oficial, nome_completo, nome_guerra, posto_graduacao, caminho_assinatura):
    """Atualiza as informações de um oficial existente."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE oficiais
    SET nome_completo = ?, nome_guerra = ?, posto_graduacao = ?, caminho_assinatura = ?
    WHERE id = ?
    """, (nome_completo, nome_guerra, posto_graduacao, caminho_assinatura, id_oficial))
    conn.commit()
    conn.close()

def listar_oficiais():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome_completo, nome_guerra, posto_graduacao FROM oficiais ORDER BY nome_guerra")
    oficiais = cursor.fetchall()
    conn.close()
    return oficiais

def buscar_oficial_por_id(id_oficial):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM oficiais WHERE id = ?", (id_oficial,))
    oficial = cursor.fetchone()
    conn.close()
    return oficial

# ... (restante das funções do database.py sem alterações)
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
    cursor.execute("SELECT id, saram, nome_completo, nome_guerra, ocorrencia_gerada, status, data_abertura, data_conclusao, caminho_assinatura, id_oficial FROM patds WHERE status = ? ORDER BY id DESC", (status,))
    ocorrencias = cursor.fetchall()
    conn.close()
    return ocorrencias

def buscar_ocorrencia_por_id(patd_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, saram, nome_completo, nome_guerra, ocorrencia_gerada, status, data_abertura, data_conclusao, caminho_assinatura, id_oficial FROM patds WHERE id = ?", (patd_id,))
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

def associar_oficial_patd(patd_id, id_oficial):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE patds SET id_oficial = ? WHERE id = ?", (id_oficial, patd_id))
    conn.commit()
    conn.close()

def desassociar_oficial_patd(patd_id):
    """Reseta a associação do oficial para uma PATD."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE patds SET id_oficial = NULL WHERE id = ?", (patd_id,))
    conn.commit()
    conn.close()